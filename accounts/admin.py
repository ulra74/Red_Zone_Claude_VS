from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserActivityStats


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administración personalizada de usuarios"""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'user_type_badge', 'is_active', 'date_joined'
    )
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('user_type', 'created_at')
        }),
    )
    
    readonly_fields = ('created_at', 'date_joined', 'last_login')
    
    def user_type_badge(self, obj):
        """Muestra el tipo de usuario con un badge colorido"""
        colors = {
            'admin': '#dc3545',  # Rojo
            'student': '#007bff'  # Azul
        }
        color = colors.get(obj.user_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'Tipo de Usuario'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related()


@admin.register(UserActivityStats)
class UserActivityStatsAdmin(admin.ModelAdmin):
    """Administración de estadísticas de actividad de usuarios"""
    
    list_display = (
        'user', 'current_streak', 'best_streak', 'total_exams_completed',
        'total_exams_retaken', 'last_exam_date', 'activity_level_badge'
    )
    list_filter = ('last_exam_date', 'current_streak', 'best_streak')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-current_streak', '-best_streak', '-total_exams_completed')
    readonly_fields = ('created_at', 'updated_at', 'last_activity_date')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Estadísticas de Exámenes', {
            'fields': ('total_exams_completed', 'total_exams_retaken')
        }),
        ('Racha de Actividad', {
            'fields': ('current_streak', 'best_streak', 'streak_start_date')
        }),
        ('Fechas Importantes', {
            'fields': ('last_exam_date', 'last_activity_date')
        }),
        ('Puntuaciones', {
            'fields': ('streak_bonus_points', 'consistency_bonus_points', 'inactivity_penalty_points')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def activity_level_badge(self, obj):
        """Muestra el nivel de actividad con un badge colorido"""
        level_info = obj.get_activity_level()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{} {}</span>',
            level_info['color'],
            level_info['icon'],
            level_info['name']
        )
    activity_level_badge.short_description = 'Nivel de Actividad'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related('user')