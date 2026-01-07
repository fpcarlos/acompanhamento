from django.contrib import admin
from django.urls import path, include
from auditoria import api as auditoria_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auditoria.urls')),
    path('api/', include(auditoria_api.router.urls)),
    path('paf/', include('paf.urls')),
]
