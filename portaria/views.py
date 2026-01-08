from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from .models import PortariaFiscalizacao, TipoFiscalizacao, TipoPortaria, StatusPortariaFiscalizacao, Entidade
from .forms import PortariaForm
from django.http import JsonResponse
from .models import Entidade
from django.core.paginator import Paginator
from django.db.models import Q


class PortariaListView(ListView):
    model = PortariaFiscalizacao
    template_name = 'portaria/portaria_list.html'
    context_object_name = 'portarias'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('tipo_fiscalizacao', 'tipo_portaria', 'status_portaria').prefetch_related('entidades').order_by('-data_criacao')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(numero_portaria__icontains=q) | Q(objetivo__icontains=q) | Q(deliberacao__icontains=q) | Q(numero_processo_sei__icontains=q) | Q(ano_processo_sei__icontains=q) | Q(entidades__nome__icontains=q)).distinct()

        tipo_fiscalizacao = self.request.GET.get('tipo_fiscalizacao')
        if tipo_fiscalizacao:
            qs = qs.filter(tipo_fiscalizacao_id=tipo_fiscalizacao)

        tipo_portaria = self.request.GET.get('tipo_portaria')
        if tipo_portaria:
            qs = qs.filter(tipo_portaria_id=tipo_portaria)

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status_portaria_id=status)

        entidade = self.request.GET.get('entidade')
        if entidade:
            qs = qs.filter(entidades__pk=entidade)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_fiscalizacoes'] = TipoFiscalizacao.objects.filter(situacao_tipo_fiscalizacao=True)
        ctx['tipo_portarias'] = TipoPortaria.objects.filter(situacao_tipo_portaria=True)
        ctx['status_portarias'] = StatusPortariaFiscalizacao.objects.filter(ativo=True)
        ctx['entidades_list'] = Entidade.objects.filter(ativo=True)[:200]
        return ctx


class PortariaCreateView(CreateView):
    model = PortariaFiscalizacao
    form_class = PortariaForm
    template_name = 'portaria/portaria_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.usuario_criacao = self.request.user
        obj.save()
        form.save_m2m()
        messages.success(self.request, f'Portaria {obj.numero_portaria} criada com sucesso')
        return redirect('portaria:portaria-detail', pk=obj.pk)


class PortariaDetailView(DetailView):
    model = PortariaFiscalizacao
    template_name = 'portaria/portaria_detail.html'


def entidade_search(request):
    """AJAX endpoint for searching entidades (used by Select2)."""
    q = request.GET.get('q', '').strip()
    qs = Entidade.objects.filter(ativo=True)
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(sigla__icontains=q))
    paginator = Paginator(qs.order_by('nome'), 20)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)

    results = [{'id': e.pk, 'text': str(e)} for e in page_obj.object_list]
    return JsonResponse({'results': results, 'pagination': {'more': page_obj.has_next()} })
