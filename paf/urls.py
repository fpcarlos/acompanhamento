from django.urls import path
from . import views

app_name = 'paf'

urlpatterns = [
    path('', views.paf_index, name='paf-index'),
    path('import/', views.paf_import, name='paf-import'),
]
