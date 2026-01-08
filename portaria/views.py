from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from .models import PortariaFiscalizacao
from .forms import PortariaForm


class PortariaListView(ListView):
    model = PortariaFiscalizacao
    template_name = 'portaria/portaria_list.html'
    context_object_name = 'portarias'
    paginate_by = 25


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
