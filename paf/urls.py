from django.urls import path
from . import views

app_name = 'paf'

urlpatterns = [
    path('', views.paf_index, name='paf-index'),
    path('import/', views.paf_import, name='paf-import'),
    path('imports/', views.paf_imports_list, name='paf-imports-list'),
    path('imports/<int:pk>/', views.paf_import_detail, name='paf-import-detail'),
]
