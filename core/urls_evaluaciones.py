# core/urls_evaluaciones.py - ARCHIVO RENOMBRADO Y CORREGIDO

from django.urls import path
from . import views_evaluaciones

app_name = 'evaluaciones'

urlpatterns = [
    # ============================================================================
    # RUTAS PARA ESTUDIANTES
    # ============================================================================
    
    # Lista y detalle de exámenes
    path('', views_evaluaciones.ExamenListView.as_view(), name='examen_list'),
    path('<int:pk>/', views_evaluaciones.ExamenDetailView.as_view(), name='examen_detail'),
    
    # Realizar exámenes
    path('<int:pk>/iniciar/', views_evaluaciones.IniciarExamenView.as_view(), name='iniciar_examen'),
    path('realizar/<int:pk>/', views_evaluaciones.RealizarExamenView.as_view(), name='realizar_examen'),
    path('resultado/<int:pk>/', views_evaluaciones.ResultadoExamenView.as_view(), name='resultado_examen'),
    
    # AJAX para exámenes
    path('api/guardar-respuesta/', views_evaluaciones.guardar_respuesta, name='guardar_respuesta'),
    path('api/finalizar-examen/', views_evaluaciones.finalizar_examen, name='finalizar_examen'),
    
    # ============================================================================
    # RUTAS DE ADMINISTRACIÓN
    # ============================================================================
    
    # Gestión de exámenes
    path('admin/', views_evaluaciones.AdminExamenListView.as_view(), name='admin_examen_list'),
    path('admin/crear/', views_evaluaciones.AdminExamenCreateView.as_view(), name='admin_examen_create'),
    path('admin/<int:pk>/editar/', views_evaluaciones.AdminExamenUpdateView.as_view(), name='admin_examen_update'),
    path('admin/<int:pk>/eliminar/', views_evaluaciones.AdminExamenDeleteView.as_view(), name='admin_examen_delete'),
    
    # Estadísticas
    path('admin/<int:pk>/estadisticas/', views_evaluaciones.EstadisticasExamenView.as_view(), name='admin_estadisticas_examen'),
    
    # Banco de preguntas
    path('admin/preguntas/', views_evaluaciones.BancoPreguntaListView.as_view(), name='admin_banco_preguntas'),
    
    # ============================================================================
    # RUTAS FUTURAS (PREPARADAS PARA EXPANSIÓN)
    # ============================================================================
    
    # Gestión de categorías
    # path('admin/categorias/', views_evaluaciones.CategoriaListView.as_view(), name='admin_categoria_list'),
    # path('admin/categorias/crear/', views_evaluaciones.CategoriaCreateView.as_view(), name='admin_categoria_create'),
    
    # Gestión de preguntas
    # path('admin/preguntas/crear/', views_evaluaciones.BancoPreguntaCreateView.as_view(), name='admin_pregunta_create'),
    # path('admin/preguntas/<int:pk>/editar/', views_evaluaciones.BancoPreguntaUpdateView.as_view(), name='admin_pregunta_update'),
    # path('admin/preguntas/<int:pk>/eliminar/', views_evaluaciones.BancoPreguntaDeleteView.as_view(), name='admin_pregunta_delete'),
    
    # Importación masiva
    # path('admin/preguntas/importar/', views_evaluaciones.ImportarPreguntasView.as_view(), name='admin_importar_preguntas'),
    
    # Reportes avanzados
    # path('admin/reportes/', views_evaluaciones.ReportesView.as_view(), name='admin_reportes'),
    # path('admin/reportes/estudiante/<int:user_id>/', views_evaluaciones.ReporteEstudianteView.as_view(), name='admin_reporte_estudiante'),
]