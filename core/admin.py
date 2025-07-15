# core/admin.py - ACTUALIZADO con gestión de relación Oposicion-Tema

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Oposicion, Tema, TemaOposicion, ArchivoOposicion, ArchivoTema, 
    DescargaArchivo, ProgresoEstudiante
)

# Importar modelos de evaluaciones
from .models_evaluaciones import (
    Categoria, BancoPregunta, RespuestaPregunta, Examen, 
    IntentosExamen, PreguntaExamen, RespuestaEstudiante, EstadisticasExamen
)


# ============================================================================
# ADMIN PARA EVALUACIONES (mantener código existente)
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


# ============================================================================
# ADMIN PARA GESTIÓN DE ARCHIVOS
# ============================================================================

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


# ============================================================================
# ADMIN PARA RELACIÓN TEMA-OPOSICIÓN
# ============================================================================

class TemaOposicionInline(admin.TabularInline):
    """Inline para gestionar temas en oposiciones"""
    model = TemaOposicion
    extra = 1
    fields = ('tema', 'orden_en_oposicion', 'es_obligatorio_en_oposicion', 'peso_en_oposicion', 'fecha_inicio_tema', 'fecha_fin_tema')
    ordering = ('orden_en_oposicion',)
    autocomplete_fields = ('tema',)


class OposicionTemaInline(admin.TabularInline):
    """Inline para gestionar oposiciones en temas"""
    model = TemaOposicion
    extra = 1
    fields = ('oposicion', 'orden_en_oposicion', 'es_obligatorio_en_oposicion', 'peso_en_oposicion')
    ordering = ('orden_en_oposicion',)
    autocomplete_fields = ('oposicion',)


# ============================================================================
# ADMIN PRINCIPAL PARA OPOSICIONES Y TEMAS
# ============================================================================

@admin.register(Oposicion)
class OposicionAdmin(admin.ModelAdmin):
    """Administración de Oposiciones MEJORADA"""
    
    list_display = (
        'nombre', 'fecha_convocatoria', 'temas_count', 'estudiantes_count', 
        'archivos_count', 'examenes_count', 'created_at'
    )
    list_filter = ('fecha_convocatoria', 'created_at')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_convocatoria'
    ordering = ('-created_at',)
    inlines = [TemaOposicionInline, ArchivoOposicionInline]
    
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
    
    def temas_count(self, obj):
        """Cuenta los temas de la oposición"""
        count = obj.temas.count()
        if count > 0:
            url = reverse('admin:core_tema_changelist') + f'?oposiciones__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="background-color: #17a2b8; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px; text-decoration: none;">{} temas</a>',
                url, count
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">0 temas</span>'
        )
    temas_count.short_description = 'Temas'
    
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
        try:
            count = obj.examen_set.count()
            activos = obj.examen_set.filter(activo=True, publicado=True).count()
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">{} total / {} activos</span>',
                count, activos
            )
        except:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">0 exámenes</span>'
            )
    examenes_count.short_description = 'Exámenes'
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos', 'temas'
        )


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """Administración de Temas MEJORADA"""
    
    list_display = (
        'nombre', 'oposiciones_count', 'estudiantes_count', 'archivos_count', 
        'examenes_count', 'orden', 'created_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'created_at'
    ordering = ('orden', 'nombre')
    inlines = [OposicionTemaInline, ArchivoTemaInline]
    list_editable = ('orden',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden',)
        }),
        ('Relaciones', {
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
    
    def oposiciones_count(self, obj):
        """Cuenta las oposiciones del tema"""
        count = obj.oposiciones.count()
        if count > 0:
            url = reverse('admin:core_oposicion_changelist') + f'?temas__id__exact={obj.id}'
            oposiciones_list = ", ".join([op.nombre for op in obj.oposiciones.all()[:2]])
            if count > 2:
                oposiciones_list += f" (+{count-2} más)"
            
            return format_html(
                '<a href="{}" style="background-color: #dc3545; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px; text-decoration: none;" title="{}">{} oposiciones</a>',
                url, oposiciones_list, count
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">0 oposiciones</span>'
        )
    oposiciones_count.short_description = 'Oposiciones'
    
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
        try:
            count = obj.examen_set.count()
            activos = obj.examen_set.filter(activo=True, publicado=True).count()
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">{} total / {} activos</span>',
                count, activos
            )
        except:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">0 exámenes</span>'
            )
    examenes_count.short_description = 'Exámenes'
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos', 'oposiciones'
        )


# ============================================================================
# ADMIN PARA MODELO INTERMEDIO
# ============================================================================

@admin.register(TemaOposicion)
class TemaOposicionAdmin(admin.ModelAdmin):
    """Administración de la relación Tema-Oposición"""
    
    list_display = ('tema', 'oposicion', 'orden_en_oposicion', 'es_obligatorio_en_oposicion', 'peso_en_oposicion', 'created_at')
    list_filter = ('es_obligatorio_en_oposicion', 'peso_en_oposicion', 'oposicion', 'created_at')
    search_fields = ('tema__nombre', 'oposicion__nombre')
    ordering = ('oposicion', 'orden_en_oposicion')
    autocomplete_fields = ('tema', 'oposicion')
    
    fieldsets = (
        ('Relación', {
            'fields': ('tema', 'oposicion')
        }),
        ('Configuración en Oposición', {
            'fields': ('orden_en_oposicion', 'es_obligatorio_en_oposicion', 'peso_en_oposicion')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio_tema', 'fecha_fin_tema'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ADMIN PARA ARCHIVOS Y DESCARGAS
# ============================================================================

@admin.register(ArchivoOposicion)
class ArchivoOposicionAdmin(admin.ModelAdmin):
    """Administración de Archivos de Oposición"""
    
    list_display = ('nombre', 'oposicion', 'tipo', 'tamaño_legible', 'descargas', 'es_publico', 'subido_por', 'fecha_subida')
    list_filter = ('tipo', 'es_publico', 'fecha_subida', 'oposicion')
    search_fields = ('nombre', 'descripcion', 'oposicion__nombre')
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida')
    ordering = ('-fecha_subida',)
    date_hierarchy = 'fecha_subida'


@admin.register(ArchivoTema)
class ArchivoTemaAdmin(admin.ModelAdmin):
    """Administración de Archivos de Tema"""
    
    list_display = ('nombre', 'tema', 'tipo', 'tamaño_legible', 'descargas', 'orden', 'es_publico', 'subido_por', 'fecha_subida')
    list_filter = ('tipo', 'es_publico', 'fecha_subida', 'tema')
    search_fields = ('nombre', 'descripcion', 'tema__nombre')
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida')
    ordering = ('tema', 'orden', '-fecha_subida')
    date_hierarchy = 'fecha_subida'
    list_editable = ('orden',)


@admin.register(DescargaArchivo)
class DescargaArchivoAdmin(admin.ModelAdmin):
    """Administración de Registro de Descargas"""
    
    list_display = ('usuario', 'archivo_info', 'fecha_descarga', 'ip_address')
    list_filter = ('fecha_descarga',)
    search_fields = ('usuario__username', 'archivo_oposicion__nombre', 'archivo_tema__nombre')
    readonly_fields = ('usuario', 'archivo_oposicion', 'archivo_tema', 'fecha_descarga', 'ip_address')
    ordering = ('-fecha_descarga',)
    date_hierarchy = 'fecha_descarga'
    
    def archivo_info(self, obj):
        """Información del archivo descargado"""
        archivo = obj.archivo_oposicion or obj.archivo_tema
        if archivo:
            tipo = "Oposición" if obj.archivo_oposicion else "Tema"
            return format_html(
                '<strong>{}</strong><br><small>{}: {}</small>',
                archivo.nombre,
                tipo,
                archivo.oposicion.nombre if obj.archivo_oposicion else archivo.tema.nombre
            )
        return "Archivo eliminado"
    archivo_info.short_description = 'Archivo'


@admin.register(ProgresoEstudiante)
class ProgresoEstudianteAdmin(admin.ModelAdmin):
    """Administración de Progreso de Estudiantes"""
    
    list_display = ('estudiante', 'contenido_info', 'porcentaje_completado', 'completado', 'ultima_actividad')
    list_filter = ('completado', 'ultima_actividad', 'oposicion', 'tema')
    search_fields = ('estudiante__username', 'oposicion__nombre', 'tema__nombre')
    readonly_fields = ('ultima_actividad',)
    ordering = ('-ultima_actividad',)
    date_hierarchy = 'ultima_actividad'
    
    def contenido_info(self, obj):
        """Información del contenido"""
        if obj.oposicion:
            return format_html(
                '<strong>Oposición:</strong> {}<br><small>{} temas</small>',
                obj.oposicion.nombre,
                obj.oposicion.temas.count()
            )
        elif obj.tema:
            return format_html(
                '<strong>Tema:</strong> {}<br><small>{} oposiciones</small>',
                obj.tema.nombre,
                obj.tema.oposiciones.count()
            )
        return "Contenido eliminado"
    contenido_info.short_description = 'Contenido'


# Personalización del sitio admin
admin.site.site_header = 'Red Zone Academy - Administración'
admin.site.site_title = 'RZA Admin'
admin.site.index_title = 'Panel de Administración'

# Configurar búsqueda automática para mejor UX
Tema.search_fields = ['nombre', 'descripcion']
Oposicion.search_fields = ['nombre', 'descripcion']