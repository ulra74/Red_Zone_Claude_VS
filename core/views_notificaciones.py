# core/views_notificaciones.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django import forms

from .models import Notificacion, LecturaNotificacion, Oposicion, TipoNotificacion
from .views import AdminRequiredMixin


# =================== FORMULARIOS ===================

class NotificacionForm(forms.ModelForm):
    """Formulario para crear notificaciones"""
    
    class Meta:
        model = Notificacion
        fields = [
            'titulo', 'mensaje', 'tipo', 'es_urgente', 
            'requiere_confirmacion', 'enlace_url', 'enlace_texto',
            'fecha_expiracion'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la notificación'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe aquí el mensaje para los estudiantes...'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'es_urgente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requiere_confirmacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enlace_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com (opcional)'
            }),
            'enlace_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto del enlace (ej: Ver más información)'
            }),
            'fecha_expiracion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].help_text = "Título que verán los estudiantes"
        self.fields['mensaje'].help_text = "Mensaje principal de la notificación"
        self.fields['tipo'].help_text = "Tipo de notificación (afecta el color y el icono)"
        self.fields['es_urgente'].help_text = "Las notificaciones urgentes aparecen destacadas"
        self.fields['requiere_confirmacion'].help_text = "El estudiante debe confirmar que ha leído"
        self.fields['enlace_url'].help_text = "URL opcional para más información"
        self.fields['enlace_texto'].help_text = "Texto que aparecerá en el botón del enlace"
        self.fields['fecha_expiracion'].help_text = "La notificación se ocultará después de esta fecha"


# =================== VISTAS PARA ADMINISTRADORES ===================

class EnviarNotificacionView(AdminRequiredMixin, CreateView):
    """Vista para enviar notificaciones a estudiantes de una oposición"""
    model = Notificacion
    form_class = NotificacionForm
    template_name = 'core/notificaciones/enviar_notificacion.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.oposicion = get_object_or_404(Oposicion, pk=kwargs['oposicion_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.oposicion = self.oposicion
        form.instance.enviado_por = self.request.user
        
        # Contar estudiantes objetivo
        estudiantes_count = self.oposicion.alumnos_con_acceso.filter(user_type='student').count()
        
        messages.success(
            self.request,
            f'Notificación "{form.instance.titulo}" enviada a {estudiantes_count} estudiantes de {self.oposicion.nombre}.'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:oposicion_detail', kwargs={'pk': self.oposicion.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oposicion'] = self.oposicion
        context['title'] = f'Enviar Notificación - {self.oposicion.nombre}'
        context['estudiantes_count'] = self.oposicion.alumnos_con_acceso.filter(user_type='student').count()
        return context


class NotificacionesOposicionView(AdminRequiredMixin, ListView):
    """Lista de notificaciones enviadas para una oposición"""
    model = Notificacion
    template_name = 'core/notificaciones/notificaciones_oposicion.html'
    context_object_name = 'notificaciones'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        self.oposicion = get_object_or_404(Oposicion, pk=kwargs['oposicion_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.oposicion.notificaciones.select_related('enviado_por').prefetch_related('lecturas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oposicion'] = self.oposicion
        context['title'] = f'Notificaciones - {self.oposicion.nombre}'
        
        # Estadísticas
        context['total_notificaciones'] = self.get_queryset().count()
        context['notificaciones_activas'] = self.get_queryset().filter(activa=True).count()
        
        return context


class NotificacionDetailView(AdminRequiredMixin, DetailView):
    """Detalle de una notificación con estadísticas de lectura"""
    model = Notificacion
    template_name = 'core/notificaciones/notificacion_detail.html'
    context_object_name = 'notificacion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notificacion = self.object
        
        context['title'] = f'Notificación: {notificacion.titulo}'
        context['lecturas'] = notificacion.lecturas.select_related('usuario').order_by('-fecha_lectura')
        context['estudiantes_sin_leer'] = notificacion.estudiantes_objetivo.exclude(
            id__in=notificacion.lecturas.values_list('usuario_id', flat=True)
        )
        
        return context


# =================== VISTAS PARA ESTUDIANTES ===================

class MisNotificacionesView(LoginRequiredMixin, ListView):
    """Vista de notificaciones para estudiantes"""
    model = Notificacion
    template_name = 'core/notificaciones/mis_notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 15
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_student():
            messages.error(request, 'Solo los estudiantes pueden ver esta página.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        # Obtener notificaciones de las oposiciones del usuario
        user_oposiciones = self.request.user.oposiciones_acceso.all()
        
        queryset = Notificacion.objects.filter(
            oposicion__in=user_oposiciones,
            activa=True
        ).select_related('oposicion', 'enviado_por').prefetch_related('lecturas')
        
        # Filtrar las expiradas
        queryset = queryset.filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gt=timezone.now())
        )
        
        # Ordenar por urgentes primero, luego por fecha
        return queryset.order_by('-es_urgente', '-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Notificaciones'
        
        # Contar notificaciones no leídas
        context['no_leidas'] = self.get_queryset().exclude(
            lecturas__usuario=self.request.user
        ).count()
        
        # Marcar cuáles ha leído el usuario
        notificaciones_leidas = set(
            LecturaNotificacion.objects.filter(
                usuario=self.request.user,
                notificacion__in=context['notificaciones']
            ).values_list('notificacion_id', flat=True)
        )
        
        for notificacion in context['notificaciones']:
            notificacion.leida_por_usuario = notificacion.id in notificaciones_leidas
        
        return context


# =================== VISTAS AJAX ===================

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Marca una notificación como leída (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        notificacion = get_object_or_404(Notificacion, id=notificacion_id)
        
        # Verificar que el usuario puede ver esta notificación
        if not notificacion.es_visible_para(request.user):
            return JsonResponse({'success': False, 'error': 'Sin permisos'})
        
        # Marcar como leída
        created = notificacion.marcar_como_leida(request.user)
        
        return JsonResponse({
            'success': True,
            'nueva_lectura': created,
            'total_leidas': notificacion.total_leidas,
            'porcentaje_lectura': notificacion.porcentaje_lectura
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def obtener_notificaciones_no_leidas(request):
    """Obtiene el número de notificaciones no leídas (AJAX)"""
    if not request.user.is_student():
        return JsonResponse({'success': False, 'count': 0})
    
    try:
        # Obtener oposiciones del usuario
        user_oposiciones = request.user.oposiciones_acceso.all()
        
        # Contar notificaciones no leídas
        count = Notificacion.objects.filter(
            oposicion__in=user_oposiciones,
            activa=True
        ).exclude(
            lecturas__usuario=request.user
        ).filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gt=timezone.now())
        ).count()
        
        return JsonResponse({'success': True, 'count': count})
        
    except Exception as e:
        return JsonResponse({'success': False, 'count': 0, 'error': str(e)})


@login_required 
def alternar_notificacion_activa(request, notificacion_id):
    """Activa/desactiva una notificación (solo admins)"""
    if not request.user.is_admin():
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        notificacion = get_object_or_404(Notificacion, id=notificacion_id)
        notificacion.activa = not notificacion.activa
        notificacion.save()
        
        estado = 'activada' if notificacion.activa else 'desactivada'
        
        return JsonResponse({
            'success': True,
            'activa': notificacion.activa,
            'mensaje': f'Notificación {estado} exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})