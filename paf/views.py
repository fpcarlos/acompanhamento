from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from .forms import PAFUploadForm
from .models import PAFImport, PAFAction, UnidadeTecnica
from .utils import read_table_from_file, validate_columns, REQUIRED_COLUMNS
from .utils import map_headers
from .forms import ConfirmImportForm
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404


@login_required
def paf_index(request):
    year = request.GET.get('year')
    qs = PAFAction.objects.all().order_by('-ano', 'codigo_acao')
    if year:
        qs = qs.filter(ano=year)
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    ctx = {'actions_page': paginator.get_page(page), 'year': year}
    return render(request, 'paf/paf_index.html', ctx)


@login_required
def paf_imports_list(request):
    qs = PAFImport.objects.all().order_by('-uploaded_at')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    ctx = {'imports_page': paginator.get_page(page)}
    return render(request, 'paf/paf_imports_list.html', ctx)


@login_required
def paf_import_detail(request, pk):
    imp = get_object_or_404(PAFImport, pk=pk)
    # summary contains 'processed' and 'errors' list
    summary = imp.summary or {}
    errors = summary.get('errors', []) if isinstance(summary, dict) else []
    return render(request, 'paf/paf_import_detail.html', {'import': imp, 'errors': errors, 'summary': summary})


@login_required
def paf_import(request):
    if request.method == 'POST':
        # Determine if this is the confirmation POST (has 'confirm' or import_id) or initial upload
        if 'confirm' in request.POST or 'import_id' in request.POST:
            confirm_form = ConfirmImportForm(request.POST)
            if confirm_form.is_valid():
                import_id = confirm_form.cleaned_data['import_id']
                replace_existing = confirm_form.cleaned_data.get('replace_existing', False)
                imp = get_object_or_404(PAFImport, pk=import_id)
                # Re-open stored file and process all rows
                with imp.file.open('rb') as fh:
                    rows, errors = read_table_from_file(fh)
                if errors:
                    imp.processed = True
                    imp.summary = {'processed': 0, 'errors': [{'line': 0, 'error': 'Erro ao ler o arquivo: ' + '; '.join(errors)}]}
                    imp.save()
                    messages.error(request, 'Erro ao ler o arquivo: ' + '; '.join(errors))
                    return redirect(reverse('paf:paf-import'))

                headers = list(rows[0].keys()) if rows else []
                mapping, missing = map_headers(headers)
                if missing:
                    imp.processed = True
                    imp.summary = {'processed': 0, 'errors': [{'line': 0, 'error': 'Layout inválido. Colunas faltando: ' + ', '.join(missing)}]}
                    imp.save()
                    messages.error(request, 'Layout inválido. Colunas faltando: ' + ', '.join(missing))
                    return redirect(reverse('paf:paf-import'))

                # Check replace_existing rules
                year_candidate = rows[0].get(mapping.get('Ano'))
                try:
                    year_v = int(year_candidate)
                except Exception:
                    year_v = None

                if replace_existing and year_v is not None:
                    existing_qs = PAFAction.objects.filter(ano=year_v)
                    if existing_qs.filter(status=PAFAction.Status.EM_EXECUCAO).exists():
                        imp.processed = True
                        imp.summary = {'processed': 0, 'errors': [{'line': 0, 'error': 'Não é possível substituir: existem ações em execução para o exercício.'}]}
                        imp.save()
                        messages.error(request, 'Não é possível substituir: existem ações em execução para o exercício.')
                        return redirect(reverse('paf:paf-import'))
                    else:
                        existing_qs.delete()

                processed = 0
                line_errors = []
                for idx, r in enumerate(rows, start=2):
                    # Resolve fields using mapping
                    codigo = r.get(mapping.get('Código da Ação'))
                    unidade_nome = r.get(mapping.get('Unidade Técnica Responsável'))
                    meta = r.get(mapping.get('Meta'))
                    ano = r.get(mapping.get('Ano'))

                    if not codigo or not unidade_nome:
                        line_errors.append({'line': idx, 'error': 'Código ou Unidade Técnica ausente'})
                        continue
                    try:
                        ano_v = int(ano)
                    except Exception:
                        line_errors.append({'line': idx, 'error': 'Ano inválido'})
                        continue

                    # Normalize meta
                    meta_str = str(meta).strip() if meta is not None else ''
                    ms = meta_str.replace(' ', '')
                    if '.' in ms and ',' in ms:
                        ms = ms.replace('.', '').replace(',', '.')
                    elif ',' in ms:
                        ms = ms.replace(',', '.')
                    try:
                        float(ms)
                    except Exception:
                        line_errors.append({'line': idx, 'error': 'Meta inválida'})
                        continue

                    # Unidade matching using normalize strategy
                    unidade_key = str(unidade_nome).strip() if unidade_nome is not None else ''
                    unidade = None
                    if unidade_key:
                        for ut in UnidadeTecnica.objects.all():
                            from paf.utils import normalize_str
                            if normalize_str(ut.codigo) == normalize_str(unidade_key) or normalize_str(ut.nome) == normalize_str(unidade_key):
                                unidade = ut
                                break
                    if not unidade:
                        line_errors.append({'line': idx, 'error': 'Unidade Técnica não encontrada'})
                        continue

                    # Check duplicate
                    if PAFAction.objects.filter(codigo_acao=codigo, ano=ano_v).exists():
                        line_errors.append({'line': idx, 'error': 'Duplicidade de código_acao para o mesmo exercício'})
                        continue

                    # Create action
                    PAFAction.objects.create(
                        codigo_acao=codigo,
                        area_atuacao=r.get(mapping.get('Área de Atuação')),
                        descricao=r.get(mapping.get('Descrição da Ação')) or '',
                        unidade_tecnica=unidade,
                        tipo_produto=r.get(mapping.get('Tipo de Produto / Instrumento')) or '',
                        indicador=r.get(mapping.get('Indicador')) or '',
                        meta=str(r.get(mapping.get('Meta'))),
                        ano=ano_v,
                        status=PAFAction.Status.VIGENTE,
                        criado_por=request.user,
                    )
                    processed += 1

                imp.processed = True
                imp.summary = {'processed': processed, 'errors': line_errors}
                imp.save()
                if line_errors:
                    messages.warning(request, f'Importação parcial: {processed} linhas processadas, {len(line_errors)} falhas.')
                else:
                    messages.success(request, f'Importação concluída: {processed} ações adicionadas.')
                return redirect(reverse('paf:paf-imports-list'))
            else:
                messages.error(request, 'Formulário de confirmação inválido')
                return redirect(reverse('paf:paf-import'))
        else:
            form = PAFUploadForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.cleaned_data['file']
                replace_existing = form.cleaned_data['replace_existing']
                from io import BytesIO
                from django.core.files.base import ContentFile

                data = f.read()
                tmp = BytesIO(data)
                tmp.name = f.name
                rows, errors = read_table_from_file(tmp)
                if errors:
                    messages.error(request, 'Erro ao ler o arquivo: ' + '; '.join(errors))
                    return redirect(reverse('paf:paf-index'))

                headers = list(rows[0].keys()) if rows else []
                mapping, missing = map_headers(headers)
                if missing:
                    messages.error(request, 'Layout inválido. Colunas faltando: ' + ', '.join(missing))
                    return redirect(reverse('paf:paf-index'))

                # Create an import record and save file but do not process yet
                import_record = PAFImport.objects.create(uploaded_by=request.user, year=int(rows[0].get(mapping.get('Ano')) or 0))
                import_record.file.save(f.name, ContentFile(data))
                # Prepare preview rows (first 5)
                preview_rows = rows[:5]
                confirm_form = ConfirmImportForm(initial={'import_id': import_record.id, 'replace_existing': replace_existing, 'confirm': True})
                return render(request, 'paf/paf_import_preview.html', {'import': import_record, 'preview_rows': preview_rows, 'mapping': mapping, 'confirm_form': confirm_form})
    else:
        form = PAFUploadForm()
    return render(request, 'paf/paf_import.html', {'form': form, 'required_columns': REQUIRED_COLUMNS})
