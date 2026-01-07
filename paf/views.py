from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from .forms import PAFUploadForm
from .models import PAFImport, PAFAction, UnidadeTecnica
from .utils import read_table_from_file, validate_columns, REQUIRED_COLUMNS
from django.core.paginator import Paginator
from django.db import transaction


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
def paf_import(request):
    if request.method == 'POST':
        form = PAFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            replace_existing = form.cleaned_data['replace_existing']
            # Read file bytes into memory to avoid closed file issues when saving
            from io import BytesIO
            from django.core.files.base import ContentFile

            data = f.read()
            tmp = BytesIO(data)
            tmp.name = f.name
            rows, errors = read_table_from_file(tmp)
            if errors:
                messages.error(request, 'Erro ao ler o arquivo: ' + '; '.join(errors))
                return redirect(reverse('paf:paf-index'))

            # Validate headers
            headers = rows[0].keys() if rows else []
            missing = validate_columns(headers)
            if missing:
                messages.error(request, 'Layout inválido. Colunas faltando: ' + ', '.join(missing))
                return redirect(reverse('paf:paf-index'))

            # Process rows: validation per-line
            import_record = PAFImport.objects.create(uploaded_by=request.user, year=int(rows[0].get('Ano') or 0))
            import_record.file.save(f.name, ContentFile(data))
            processed = 0
            line_errors = []
            for idx, r in enumerate(rows, start=2):
                # Validate required fields
                codigo = r.get('Código da Ação')
                unidade_nome = r.get('Unidade Técnica Responsável')
                meta = r.get('Meta')
                ano = r.get('Ano')
                # Basic validations
                if not codigo or not unidade_nome:
                    line_errors.append({'line': idx, 'error': 'Código ou Unidade Técnica ausente'})
                    continue
                try:
                    ano_v = int(ano)
                except Exception:
                    line_errors.append({'line': idx, 'error': 'Ano inválido'})
                    continue
                # Check meta numeric
                try:
                    float(meta)
                except Exception:
                    line_errors.append({'line': idx, 'error': 'Meta inválida'})
                    continue
                # Find unidade tecnica
                try:
                    unidade = UnidadeTecnica.objects.get(nome=unidade_nome)
                except UnidadeTecnica.DoesNotExist:
                    line_errors.append({'line': idx, 'error': 'Unidade Técnica não encontrada'})
                    continue

                # Check duplicate
                if PAFAction.objects.filter(codigo_acao=codigo, ano=ano_v).exists():
                    line_errors.append({'line': idx, 'error': 'Duplicidade de código_acao para o mesmo exercício'})
                    continue

                # Create action
                PAFAction.objects.create(
                    codigo_acao=codigo,
                    area_atuacao=r.get('Área de Atuação'),
                    descricao=r.get('Descrição da Ação') or '',
                    unidade_tecnica=unidade,
                    tipo_produto=r.get('Tipo de Produto / Instrumento') or '',
                    indicador=r.get('Indicador') or '',
                    meta=str(r.get('Meta')),
                    ano=ano_v,
                    status=PAFAction.Status.VIGENTE,
                    criado_por=request.user,
                )
                processed += 1

            import_record.processed = True
            import_record.summary = {'processed': processed, 'errors': line_errors}
            import_record.save()

            if line_errors:
                messages.warning(request, f'Importação parcial: {processed} linhas processadas, {len(line_errors)} falhas.')
            else:
                messages.success(request, f'Importação concluída: {processed} ações adicionadas.')

            return redirect(reverse('paf:paf-index'))
    else:
        form = PAFUploadForm()
    return render(request, 'paf/paf_import.html', {'form': form, 'required_columns': REQUIRED_COLUMNS})
