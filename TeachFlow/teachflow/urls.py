from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Inclui URLs do app core
    path('accounts/', include('accounts.urls')),  # URLs de autenticação (se necessário)
]