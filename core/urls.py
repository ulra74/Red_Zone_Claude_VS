# core/urls.py - ACTUALIZADO con gestión de temas en oposiciones

from django.urls import path, include
from . import views
from .views_files import (
    SubirArchivoOposicionView, SubirArchivoTemaView,
    ArchivosOposicionListView, ArchivosTemaListView,
    descargar_archivo_oposicion, descargar_archivo_tema,
    EliminarArchivoOposicionView, EliminarArchivoTemaView
)

app_name = 'core'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Oposiciones
    path('oposiciones/', views.OposicionListView.as_view(), name='oposicion_list'),
    path('oposiciones/<int:pk>/', views.OposicionDetailView.as_view(), name='oposicion_detail'),
    
    # Temas
    path('temas/', views.TemaListView.as_view(), name='tema_list'),
    path('temas/<int:pk>/', views.TemaDetailView.as_view(), name='tema_detail'),
    
    # Sistema de exámenes
    path('examenes/', include('core.urls_evaluaciones')),
    
    # Sistema de exámenes test
    path('examenes-test/', views.ExamenTestListView.as_view(), name='examen_test_list'),
    path('examenes-test/configurar/', views.ExamenTestConfigView.as_view(), name='examen_config'),
    path('examenes-test/<int:examen_id>/ejecutar/', views.ExamenTestEjecutarView.as_view(), name='examen_ejecutar'),
    path('examenes-test/<int:examen_id>/responder/', views.ExamenTestRespuestaView.as_view(), name='examen_responder'),
    path('examenes-test/<int:examen_id>/finalizar/', views.ExamenTestFinalizarView.as_view(), name='examen_finalizar'),
    path('examenes-test/<int:examen_id>/resultado/', views.ExamenTestResultadoView.as_view(), name='examen_resultado'),
    path('examenes-test/<int:examen_id>/repetir/', views.ExamenTestRetakeView.as_view(), name='examen_repetir'),
    path('examenes-test/<int:examen_id>/eliminar/', views.ExamenTestDeleteView.as_view(), name='examen_eliminar'),
    path('ranking/', views.ExamenTestRankingView.as_view(), name='examen_ranking'),
    
    # Admin URLs - Oposiciones
    path('admin/oposiciones/', views.AdminOposicionListView.as_view(), name='admin_oposicion_list'),
    path('admin/oposiciones/create/', views.AdminOposicionCreateView.as_view(), name='admin_oposicion_create'),
    path('admin/oposiciones/<int:pk>/edit/', views.AdminOposicionUpdateView.as_view(), name='admin_oposicion_update'),
    path('admin/oposiciones/<int:pk>/delete/', views.AdminOposicionDeleteView.as_view(), name='admin_oposicion_delete'),
    
    # NUEVO: Gestión de temas en oposiciones
    path('admin/oposiciones/<int:pk>/temas/', views.AdminOposicionTemasView.as_view(), name='admin_oposicion_temas'),
    
    # Admin URLs - Temas
    path('admin/temas/', views.AdminTemaListView.as_view(), name='admin_tema_list'),
    path('admin/temas/create/', views.AdminTemaCreateView.as_view(), name='admin_tema_create'),
    path('admin/temas/<int:pk>/edit/', views.AdminTemaUpdateView.as_view(), name='admin_tema_update'),
    path('admin/temas/<int:pk>/delete/', views.AdminTemaDeleteView.as_view(), name='admin_tema_delete'),
    
    # Admin URLs - Apartados
    path('admin/temas/<int:tema_id>/apartados/', views.AdminApartadoListView.as_view(), name='admin_apartado_list'),
    path('admin/temas/<int:tema_id>/apartados/create/', views.AdminApartadoCreateView.as_view(), name='admin_apartado_create'),
    path('admin/apartados/<int:pk>/edit/', views.AdminApartadoUpdateView.as_view(), name='admin_apartado_update'),
    path('admin/apartados/<int:pk>/delete/', views.AdminApartadoDeleteView.as_view(), name='admin_apartado_delete'),
    
    # Admin URLs - Preguntas
    path('admin/apartados/<int:apartado_id>/preguntas/', views.AdminPreguntaListView.as_view(), name='admin_pregunta_list'),
    path('admin/apartados/<int:apartado_id>/preguntas/create/', views.AdminPreguntaCreateView.as_view(), name='admin_pregunta_create'),
    path('admin/preguntas/<int:pk>/edit/', views.AdminPreguntaUpdateView.as_view(), name='admin_pregunta_update'),
    path('admin/preguntas/<int:pk>/delete/', views.AdminPreguntaDeleteView.as_view(), name='admin_pregunta_delete'),
    
    # Gestión de usuarios (solo admin)
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/create/', views.AdminUserCreateView.as_view(), name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.AdminUserUpdateView.as_view(), name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
    
    # Sistema de Archivos - Oposiciones
    path('oposiciones/<int:oposicion_id>/archivos/', ArchivosOposicionListView.as_view(), name='archivos_oposicion_list'),
    path('oposiciones/<int:oposicion_id>/archivos/subir/', SubirArchivoOposicionView.as_view(), name='subir_archivo_oposicion'),
    path('archivos/oposicion/<int:archivo_id>/descargar/', descargar_archivo_oposicion, name='descargar_archivo_oposicion'),
    path('archivos/oposicion/<int:pk>/eliminar/', EliminarArchivoOposicionView.as_view(), name='eliminar_archivo_oposicion'),
    
    # Sistema de Archivos - Temas
    path('temas/<int:tema_id>/archivos/', ArchivosTemaListView.as_view(), name='archivos_tema_list'),
    path('temas/<int:tema_id>/archivos/subir/', SubirArchivoTemaView.as_view(), name='subir_archivo_tema'),
    path('archivos/tema/<int:archivo_id>/descargar/', descargar_archivo_tema, name='descargar_archivo_tema'),
    path('archivos/tema/<int:pk>/eliminar/', EliminarArchivoTemaView.as_view(), name='eliminar_archivo_tema'),
]