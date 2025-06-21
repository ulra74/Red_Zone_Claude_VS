from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Oposicion, Tema, ArchivoOposicion, ArchivoTema, 
    DescargaArchivo, ProgresoEstudiante
)


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
        'archivos_count', 'created_at', 'updated_at'
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
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos'
        )


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """Administración de Temas"""
    
    list_display = (
        'nombre', 'estudiantes_count', 'archivos_count', 
        'created_at', 'updated_at'
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
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related(
            'alumnos_con_acceso', 'archivos'
        )


@admin.register(ArchivoOposicion)
class ArchivoOposicionAdmin(admin.ModelAdmin):
    """Administración de Archivos de Oposiciones"""
    
    list_display = (
        'nombre', 'oposicion', 'tipo', 'tamaño_display', 
        'descargas', 'es_publico', 'subido_por', 'fecha_subida'
    )
    list_filter = ('tipo', 'es_publico', 'fecha_subida', 'oposicion')
    search_fields = ('nombre', 'descripcion', 'oposicion__nombre')
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida', 'extension_display')
    ordering = ('-fecha_subida',)
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('nombre', 'descripcion', 'archivo', 'tipo', 'extension_display', 'tamaño')
        }),
        ('Configuración', {
            'fields': ('oposicion', 'es_publico', 'subido_por')
        }),
        ('Estadísticas', {
            'fields': ('descargas', 'fecha_subida'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que sube el archivo"""
        if not obj.pk:  # Solo en creación
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)
    
    def tamaño_display(self, obj):
        """Muestra el tamaño del archivo de forma legible"""
        return obj.tamaño_legible
    tamaño_display.short_description = 'Tamaño'
    
    def extension_display(self, obj):
        """Muestra la extensión del archivo"""
        ext = obj.extension
        if ext:
            color = {
                '.pdf': '#dc3545',
                '.doc': '#007bff', '.docx': '#007bff',
                '.ppt': '#fd7e14', '.pptx': '#fd7e14',
                '.mp4': '#28a745', '.avi': '#28a745', '.mov': '#28a745',
                '.mp3': '#6f42c1', '.wav': '#6f42c1'
            }.get(ext, '#6c757d')
            
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px; font-weight: bold;">{}</span>',
                color, ext.upper()
            )
        return "N/A"
    extension_display.short_description = 'Tipo'


@admin.register(ArchivoTema)
class ArchivoTemaAdmin(admin.ModelAdmin):
    """Administración de Archivos de Temas"""
    
    list_display = (
        'nombre', 'tema', 'tipo', 'orden', 'tamaño_display', 
        'descargas', 'es_publico', 'subido_por', 'fecha_subida'
    )
    list_filter = ('tipo', 'es_publico', 'fecha_subida', 'tema')
    search_fields = ('nombre', 'descripcion', 'tema__nombre')
    readonly_fields = ('tamaño', 'descargas', 'fecha_subida', 'extension_display')
    ordering = ('tema', 'orden', '-fecha_subida')
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': ('nombre', 'descripcion', 'archivo', 'tipo', 'extension_display', 'tamaño')
        }),
        ('Configuración', {
            'fields': ('tema', 'orden', 'es_publico', 'subido_por')
        }),
        ('Estadísticas', {
            'fields': ('descargas', 'fecha_subida'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que sube el archivo"""
        if not obj.pk:  # Solo en creación
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)
    
    def tamaño_display(self, obj):
        """Muestra el tamaño del archivo de forma legible"""
        return obj.tamaño_legible
    tamaño_display.short_description = 'Tamaño'
    
    def extension_display(self, obj):
        """Muestra la extensión del archivo"""
        ext = obj.extension
        if ext:
            color = {
                '.pdf': '#dc3545',
                '.doc': '#007bff', '.docx': '#007bff',
                '.ppt': '#fd7e14', '.pptx': '#fd7e14',
                '.mp4': '#28a745', '.avi': '#28a745', '.mov': '#28a745',
                '.mp3': '#6f42c1', '.wav': '#6f42c1'
            }.get(ext, '#6c757d')
            
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px; font-weight: bold;">{}</span>',
                color, ext.upper()
            )
        return "N/A"
    extension_display.short_description = 'Tipo'


@admin.register(DescargaArchivo)
class DescargaArchivoAdmin(admin.ModelAdmin):
    """Administración de Descargas de Archivos"""
    
    list_display = (
        'usuario', 'archivo_display', 'fecha_descarga', 'ip_address'
    )
    list_filter = ('fecha_descarga',)
    search_fields = (
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'archivo_oposicion__nombre', 'archivo_tema__nombre'
    )
    readonly_fields = ('usuario', 'archivo_oposicion', 'archivo_tema', 'fecha_descarga', 'ip_address')
    ordering = ('-fecha_descarga',)
    
    def archivo_display(self, obj):
        """Muestra el archivo descargado"""
        if obj.archivo_oposicion:
            return f"Oposición: {obj.archivo_oposicion.nombre}"
        elif obj.archivo_tema:
            return f"Tema: {obj.archivo_tema.nombre}"
        return "Archivo eliminado"
    archivo_display.short_description = 'Archivo'
    
    def has_add_permission(self, request):
        """No permitir añadir registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False


@admin.register(ProgresoEstudiante)
class ProgresoEstudianteAdmin(admin.ModelAdmin):
    """Administración del Progreso de Estudiantes"""
    
    list_display = (
        'estudiante', 'contenido_display', 'porcentaje_completado', 
        'tiempo_estudiado_display', 'completado', 'ultima_actividad'
    )
    list_filter = ('completado', 'ultima_actividad', 'oposicion', 'tema')
    search_fields = (
        'estudiante__username', 'estudiante__first_name', 'estudiante__last_name',
        'oposicion__nombre', 'tema__nombre'
    )
    readonly_fields = ('ultima_actividad',)
    ordering = ('-ultima_actividad',)
    
    fieldsets = (
        ('Información del Estudiante', {
            'fields': ('estudiante', 'oposicion', 'tema')
        }),
        ('Progreso', {
            'fields': ('porcentaje_completado', 'tiempo_estudiado', 'completado')
        }),
        ('Metadatos', {
            'fields': ('ultima_actividad',),
            'classes': ('collapse',)
        }),
    )
    
    def contenido_display(self, obj):
        """Muestra el contenido (oposición o tema)"""
        if obj.oposicion:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">OPO</span> {}',
                obj.oposicion.nombre
            )
        elif obj.tema:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px;">TEMA</span> {}',
                obj.tema.nombre
            )
        return "Contenido eliminado"
    contenido_display.short_description = 'Contenido'
    
    def tiempo_estudiado_display(self, obj):
        """Muestra el tiempo estudiado en formato legible"""
        if obj.tiempo_estudiado == 0:
            return "0 min"
        
        horas = obj.tiempo_estudiado // 60
        minutos = obj.tiempo_estudiado % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos} min"
    tiempo_estudiado_display.short_description = 'Tiempo Estudiado'


# Personalización del sitio admin
admin.site.site_header = 'Red Zone Academy - Administración'
admin.site.site_title = 'RZA Admin'
admin.site.index_title = 'Panel de Administración'