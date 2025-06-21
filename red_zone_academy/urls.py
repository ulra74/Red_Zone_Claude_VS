from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),
    path('auth/', include('accounts.urls')),
    path('dashboard/', include('core.urls')),
]

# Configuración para archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalización del admin
admin.site.site_header = 'Red Zone Academy - Administración'
admin.site.site_title = 'RZA Admin'
admin.site.index_title = 'Panel de Administración'