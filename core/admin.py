# core/admin.py - ACTUALIZACIÓN COMPLETA con sistema de evaluaciones

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Oposicion, Tema, ArchivoOposicion, ArchivoTema, 
    DescargaArchivo, ProgresoEstudiante
)

# Importar modelos de evaluaciones
from .models_evaluaciones import (
    Categoria, BancoPregunta, RespuestaPregunta, Examen, 
    IntentosExamen, PreguntaExamen, RespuestaEstudiante, EstadisticasExamen
)


# ============================================================================
# ADMIN PARA EVALUACIONES
# ============================================================================

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Administración de Categorías de Preguntas"""
    
    list_display = ('nombre', 'color_display', 'total_preguntas', 'orden', 'activa', 'created_at')
    list_filter = ('activa', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('orden', 'nombre')
    list_editable = ('orden', 'activa')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'color', 'orden')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    def color_display(self, obj):
        """Muestra el color de la categoría"""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def total_preguntas(self, obj):
        """Cuenta total de preguntas en la categoría"""
        count = obj.preguntas.count()
        activas = obj.preguntas.filter(activa=True).count()
        return format_html(
            '<span class="badge" style="background-color: {};">{} total / {} activas</span>',
            '#28a745' if activas > 0 else '#6c757d',
            count,
            activas
        )
    total_preguntas.short_description = 'Preguntas'


class RespuestaPreguntaInline(admin.TabularInline):
    """Inline para respuestas de pregunta"""
    model = RespuestaPregunta
    extra = 4
    max_num = 6
    fields = ('texto', 'es_correcta', 'orden', 'explicacion')
    ordering = ('orden',)


@admin.register(BancoPregunta)
class BancoPreguntaAdmin(admin.ModelAdmin):
    """Administración del Banco de Preguntas"""
    
    list_display = (
        'enunciado_corto', 'categoria', 'dificultad_display', 'puntos', 
        'estadisticas_display', 'estado_display', 'creada_por', 'created_at'
    )
    list_filter = ('categoria', 'dificultad', 'activa', 'aprobada', 'oposicion', 'tema', 'created_at')
    search_fields = ('enunciado', 'explicacion', 'categoria__nombre')
    readonly_fields = ('veces_preguntada', 'veces_acertada', 'porcentaje_acierto', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [RespuestaPreguntaInline]
    
    fieldsets = (
        ('Contenido de la Pregunta', {
            'fields': ('enunciado', 'imagen', 'explicacion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'oposicion', 'tema', 'dificultad', 'puntos', 'tiempo_estimado')
        }),
        ('Estado', {
            'fields': ('activa', 'aprobada')
        }),
        ('Estadísticas', {
            'fields': ('veces_preguntada', 'veces_acertada', 'porcentaje_acierto'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('creada_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el usuario creador"""
        if not obj.pk:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)
    
    def enunciado_corto(self, obj):
        """Muestra un enunciado truncado"""
        return f"{obj.enunciado[:60]}..." if len(obj.enunciado) > 60 else obj.enunciado
    enunciado_corto.short_description = 'Enunciado'
    
    def dificultad_display(self, obj):
        """Muestra la dificultad con color"""
        colors = {
            'facil': '#28a745',
            'medio': '#ffc107',
            'dificil': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.dificultad, '#6c757d'),
            obj.get_dificultad_display()
        )
    dificultad_display.short_description = 'Dificultad'
    
    def estadisticas_display(self, obj):
        """Muestra estadísticas de la pregunta"""
        if obj.veces_preguntada == 0:
            return format_html('<span class="text-muted">Sin datos</span>')
        
        porcentaje = obj.porcentaje_acierto
        color = '#28a745' if porcentaje >= 70 else '#ffc107' if porcentaje >= 50 else '#dc3545'
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span><br><small class="text-muted">{} usos</small>',
            color,
            porcentaje,
            obj.veces_preguntada
        )
    estadisticas_display.short_description = 'Estadísticas'
    
    def estado_display(self, obj):
        """Muestra el estado de la pregunta"""
        badges = []
        if obj.activa:
            badges.append('<span class="badge badge-success">Activa</span>')
        else:
            badges.append('<span class="badge badge-secondary">Inactiva</span>')
            
        if obj.aprobada:
            badges.append('<span class="badge badge-primary">Aprobada</span>')
        else:
            badges.append('<span class="badge badge-warning">Pendiente</span>')
            
        return format_html(' '.join(badges))
    estado_display.short_description = 'Estado'


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    """Administración de Exámenes"""
    
    list_display = (
        'titulo', 'tipo_display', 'estado_display', 'estadisticas_display',
        'config_display', 'creado_por', 'created_at'
    )
    list_filter = ('tipo', 'activo', 'publicado', 'oposicion', 'tema', 'created_at')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('creado_por', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('categorias',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('titulo', 'descripcion', 'tipo')
        }),
        ('Contexto', {
            'fields': ('oposicion', 'tema', 'categorias')
        }),
        ('Configuración del Examen', {
            'fields': (
                'numero_preguntas', 'tiempo_limite', 'puntuacion_maxima', 
                'nota_minima_aprobado', 'intentos_maximos'
            )
        }),
        ('Opciones Avanzadas', {
            'fields': (
                'preguntas_aleatorias', 'respuestas_aleatorias',
                'mostrar_resultados_inmediatos', 'permitir_revision'
            )
        }),
        ('Disponibilidad', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activo', 'publicado')
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el usuario creador"""
        if not obj.pk:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def tipo_display(self, obj):
        """Muestra el tipo con color"""
        colors = {
            'test': '#007bff',
            'simulacro': '#ffc107',
            'practica': '#17a2b8',
            'evaluacion': '#28a745'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.tipo, '#6c757d'),
            obj.get_tipo_display()
        )
    tipo_display.short_description = 'Tipo'
    
    def estado_display(self, obj):
        """Muestra el estado del examen"""
        badges = []
        
        if obj.esta_disponible:
            badges.append('<span class="badge badge-success">Disponible</span>')
        elif obj.activo and obj.publicado:
            badges.append('<span class="badge badge-warning">Programado</span>')
        elif obj.activo:
            badges.append('<span class="badge badge-info">Borrador</span>')
        else:
            badges.append('<span class="badge badge-secondary">Inactivo</span>')
            
        return format_html(' '.join(badges))
    estado_display.short_description = 'Estado'
    
    def estadisticas_display(self, obj):
        """Muestra estadísticas del examen"""
        intentos = obj.intentos.count()
        aprobados = obj.intentos.filter(aprobado=True).count()
        
        if intentos == 0:
            return format_html('<span class="text-muted">Sin intentos</span>')
        
        porcentaje_aprobados = (aprobados / intentos) * 100
        color = '#28a745' if porcentaje_aprobados >= 70 else '#ffc107' if porcentaje_aprobados >= 50 else '#dc3545'
        
        return format_html(
            '<span style="color: {};">{} / {} aprobados</span><br>'
            '<small class="text-muted">{:.1f}% éxito</small>',
            color, aprobados, intentos, porcentaje_aprobados
        )
    estadisticas_display.short_description = 'Estadísticas'
    
    def config_display(self, obj):
        """Muestra configuración básica"""
        return format_html(
            '<strong>{}</strong> preguntas<br>'
            '<strong>{}</strong> minutos<br>'
            '<strong>{}</strong> intentos',
            obj.numero_preguntas,
            obj.tiempo_limite,
            obj.intentos_maximos
        )
    config_display.short_description = 'Configuración'


@admin.register(IntentosExamen)
class IntentosExamenAdmin(admin.ModelAdmin):
    """Administración de Intentos de Examen"""
    
    list_display = (
        'estudiante', 'examen', 'resultado_display', 'tiempo_display',
        'fecha_inicio', 'completado'
    )
    list_filter = ('completado', 'aprobado', 'examen', 'fecha_inicio')
    search_fields = ('estudiante__username', 'estudiante__first_name', 'estudiante__last_name', 'examen__titulo')
    readonly_fields = (
        'fecha_inicio', 'fecha_fin', 'tiempo_empleado', 'puntuacion_obtenida',
        'porcentaje', 'aprobado', 'preguntas_correctas', 'preguntas_incorrectas',
        'preguntas_sin_responder', 'ip_address', 'user_agent'
    )
    ordering = ('-fecha_inicio',)
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información del Intento', {
            'fields': ('estudiante', 'examen', 'fecha_inicio', 'fecha_fin', 'completado')
        }),
        ('Resultados', {
            'fields': (
                'puntuacion_obtenida', 'porcentaje', 'aprobado',
                'preguntas_correctas', 'preguntas_incorrectas', 'preguntas_sin_responder'
            )
        }),
        ('Tiempo', {
            'fields': ('tiempo_empleado',)
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir añadir intentos manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir ver, no editar"""
        return False
    
    def resultado_display(self, obj):
        """Muestra el resultado del intento"""
        if not obj.completado:
            return format_html('<span class="badge badge-warning">En progreso</span>')
        
        if obj.aprobado:
            badge_class = 'badge-success'
            icon = '✓'
        else:
            badge_class = 'badge-danger'
            icon = '✗'
        
        return format_html(
            '<span class="badge {}">{} {:.1f}%</span>',
            badge_class, icon, obj.porcentaje
        )
    resultado_display.short_description = 'Resultado'
    
    def tiempo_display(self, obj):
        """Muestra información de tiempo"""
        if obj.tiempo_empleado:
            return format_html(
                '<strong>{}</strong><br><small class="text-muted">de {} min límite</small>',
                str(obj.tiempo_empleado).split('.')[0],  # Quitar microsegundos
                obj.examen.tiempo_limite
            )
        return format_html('<span class="text-muted">--</span>')
    tiempo_display.short_description = 'Tiempo'


@admin.register(RespuestaEstudiante)
class RespuestaEstudianteAdmin(admin.ModelAdmin):
    """Administración de Respuestas de Estudiantes"""
    
    list_display = ('intento_info', 'pregunta_info', 'respuesta_info', 'tiempo_respuesta', 'fecha_respuesta')
    list_filter = ('es_correcta', 'fecha_respuesta', 'intento__examen')
    search_fields = ('intento__estudiante__username', 'pregunta__enunciado')
    readonly_fields = ('intento', 'pregunta', 'respuesta_seleccionada', 'tiempo_respuesta', 'fecha_respuesta', 'es_correcta')
    ordering = ('-fecha_respuesta',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def intento_info(self, obj):
        """Información del intento"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.intento.estudiante.username,
            obj.intento.examen.titulo
        )
    intento_info.short_description = 'Estudiante/Examen'
    
    def pregunta_info(self, obj):
        """Información de la pregunta"""
        return f"{obj.pregunta.enunciado[:50]}..."
    pregunta_info.short_description = 'Pregunta'
    
    def respuesta_info(self, obj):
        """Información de la respuesta"""
        if not obj.respuesta_seleccionada:
            return format_html('<span class="text-muted">Sin responder</span>')
        
        if obj.es_correcta:
            return format_html(
                '<span class="badge badge-success">✓ Correcta</span><br><small>{}</small>',
                obj.respuesta_seleccionada.texto[:30] + '...'
            )
        else:
            return format_html(
                '<span class="badge badge-danger">✗ Incorrecta</span><br><small>{}</small>',
                obj.respuesta_seleccionada.texto[:30] + '...'
            )
    respuesta_info.short_description = 'Respuesta'


@admin.register(EstadisticasExamen)
class EstadisticasExamenAdmin(admin.ModelAdmin):
    """Administración de Estadísticas de Examen"""
    
    list_display = ('examen', 'total_intentos', 'porcentaje_aprobados_display', 'puntuacion_promedio', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('examen__titulo',)
    readonly_fields = (
        'examen', 'total_intentos', 'total_aprobados', 'total_suspensos',
        'puntuacion_promedio', 'tiempo_promedio', 'porcentaje_aprobados',
        'puntuacion_maxima', 'puntuacion_minima', 'updated_at'
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def porcentaje_aprobados_display(self, obj):
        """Muestra el porcentaje de aprobados con color"""
        porcentaje = obj.porcentaje_aprobados
        if porcentaje >= 70:
            color = '#28a745'
        elif porcentaje >= 50:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, porcentaje
        )
    porcentaje_aprobados_display.short_description = '% Aprobados'


# ============================================================================
# ADMIN EXISTENTE (mantener todo lo anterior)
# ============================================================================

# [El resto del código admin.py existente se mantiene igual...]

class ArchivoOposicionInline(admin.TabularInline):
    """Inline para archivos de oposición"""
    model = ArchivoOposicion
    extra = 0
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida')
    fields = ('nombre', 'archivo', 'tipo', 'descripcion', 'es_publico', 'tamaño', 'descargas')


class ArchivoTemaInline(admin.TabularInline):
    """Inline para archivos de tema"""
    model = ArchivoTema
    extra = 0
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida')
    fields = ('nombre', 'archivo', 'tipo', 'descripcion', 'orden', 'es_publico', 'tamaño', 'descargas')


@admin.register(Oposicion)
class OposicionAdmin(admin.ModelAdmin):
    """Administración de Oposiciones"""
    
    list_display = (
        'nombre', 'fecha_convocatoria', 'estudiantes_count', 
        'archivos_count', 'examenes_count', 'created_at', 'updated_at'
    )
    list_filter = ('fecha_convocatoria', 'created_at')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_convocatoria'
    ordering = ('-created_at',)
    inlines = [ArchivoOposicionInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'fecha_convocatoria')
        }),
        ('Acceso de Estudiantes', {
            'fields': ('alumnos_con_acceso',),
            'classes': ('wide',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('alumnos_con_acceso',)
    
    def estudiantes_count(self, obj):
        """Cuenta los estudiantes con acceso"""
        count = obj.alumnos_con_acceso.count()
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} estudiantes</span>',
            count
        )
    estudiantes_count.short_description = 'Estudiantes'
    
    def archivos_count(self, obj):
        """Cuenta los archivos de la oposición"""
        count = obj.archivos.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} archivos</span>',
            count
        )
    archivos_count.short_description = 'Archivos'
    
    def examenes_count(self, obj):
        """Cuenta los exámenes de la oposición"""
        count = obj.examen_set.count()
        activos = obj.examen_set.filter(activo=True, publicado=True).count()
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} total / {} activos</span>',
            count, activos
        )
    examenes_count.short_description = 'Exámenes'
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos', 'examen_set'
        )


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """Administración de Temas"""
    
    list_display = (
        'nombre', 'estudiantes_count', 'archivos_count', 
        'examenes_count', 'created_at', 'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('nombre',)
    date_hierarchy = 'created_at'
    ordering = ('nombre',)
    inlines = [ArchivoTemaInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre',)
        }),
        ('Acceso de Estudiantes', {
            'fields': ('alumnos_con_acceso',),
            'classes': ('wide',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('alumnos_con_acceso',)
    
    def estudiantes_count(self, obj):
        """Cuenta los estudiantes con acceso"""
        count = obj.alumnos_con_acceso.count()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} estudiantes</span>',
            count
        )
    estudiantes_count.short_description = 'Estudiantes'
    
    def archivos_count(self, obj):
        """Cuenta los archivos del tema"""
        count = obj.archivos.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} archivos</span>',
            count
        )
    archivos_count.short_description = 'Archivos'
    
    def examenes_count(self, obj):
        """Cuenta los exámenes del tema"""
        count = obj.examen_set.count()
        activos = obj.examen_set.filter(activo=True, publicado=True).count()
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{} total / {} activos</span>',
            count, activos
        )
    examenes_count.short_description = 'Exámenes'
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos', 'examen_set'
        )


# [Resto del admin existente se mantiene igual...]
# ... (ArchivoOposicionAdmin, ArchivoTemaAdmin, etc.)

# Personalización del sitio admin
admin.site.site_header = 'Red Zone Academy - Administración'
admin.site.site_title = 'RZA Admin'
admin.site.index_title = 'Panel de Administración'