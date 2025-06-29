from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Página principal
    path('', HomeView.as_view(), name='home'),
    
    # Autenticación
    path('auth/', include('accounts.urls')),
    
    # Core de la aplicación
    path('dashboard/', include('core.urls')),
    
    # Sistema de exámenes
    path('examenes/', include('core.urls_evaluaciones')),
    
    # Sistema de archivos
    #path('archivos/', include('core.urls_archivos')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
