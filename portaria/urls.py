from django.urls import path
from . import views

app_name = 'portaria'

urlpatterns = [
    path('', views.PortariaListView.as_view(), name='portaria-list'),
    path('nova/', views.PortariaCreateView.as_view(), name='portaria-create'),
    path('<int:pk>/', views.PortariaDetailView.as_view(), name='portaria-detail'),
]
