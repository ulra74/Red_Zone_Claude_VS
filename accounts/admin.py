from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


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