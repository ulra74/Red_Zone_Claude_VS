from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Oposicion, Tema


@admin.register(Oposicion)
class OposicionAdmin(admin.ModelAdmin):
    """Administración de Oposiciones"""
    
    list_display = (
        'nombre', 'fecha_convocatoria', 'estudiantes_count', 
        'created_at', 'updated_at'
    )
    list_filter = ('fecha_convocatoria', 'created_at')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha_convocatoria'
    ordering = ('-created_at',)
    
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
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related('alumnos_con_acceso')


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    """Administración de Temas"""
    
    list_display = (
        'nombre', 'estudiantes_count', 'created_at', 'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('nombre',)
    date_hierarchy = 'created_at'
    ordering = ('nombre',)
    
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
    
    def get_queryset(self, request):
        """Optimiza las consultas con prefetch"""
        return super().get_queryset(request).prefetch_related('alumnos_con_acceso')


# Personalización del sitio admin
admin.site.site_header = 'Red Zone Academy - Administración'
admin.site.site_title = 'RZA Admin'
admin.site.index_title = 'Panel de Administración'