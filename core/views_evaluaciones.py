# core/views_evaluaciones.py - ARCHIVO RENOMBRADO Y CORREGIDO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django import forms
import json
from datetime import timedelta

from core.views import AdminRequiredMixin
# CORREGIDO: Importar desde el módulo models principal
from core.models import (
    Categoria, BancoPregunta, RespuestaPregunta, Examen, 
    IntentosExamen, PreguntaExamen, RespuestaEstudiante, EstadisticasExamen,
    Oposicion, Tema
)


# ============================================================================
# VISTAS PRINCIPALES PARA ESTUDIANTES
# ============================================================================

class ExamenListView(LoginRequiredMixin, ListView):
    """Lista de exámenes disponibles para el estudiante"""
    model = Examen
    template_name = 'evaluaciones/examen_list.html'
    context_object_name = 'examenes'
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_admin():
            return Examen.objects.filter(activo=True)
        
        # Para estudiantes, filtrar por acceso a oposiciones/temas
        user = self.request.user
        return Examen.objects.filter(
            Q(activo=True, publicado=True) &
            (Q(oposicion__in=user.oposiciones_acceso.all()) |
             Q(tema__in=user.temas_acceso.all()) |
             Q(oposicion__isnull=True, tema__isnull=True))
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Exámenes Disponibles'
        
        # Agregar estadísticas del usuario
        if self.request.user.is_student():
            context['mis_intentos'] = IntentosExamen.objects.filter(
                estudiante=self.request.user
            ).count()
            context['examenes_aprobados'] = IntentosExamen.objects.filter(
                estudiante=self.request.user, 
                completado=True, 
                aprobado=True
            ).count()
        
        return context


class ExamenDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un examen y opción para iniciarlo"""
    model = Examen
    template_name = 'evaluaciones/examen_detail.html'
    context_object_name = 'examen'

    def get_queryset(self):
        if self.request.user.is_admin():
            return Examen.objects.all()
        
        user = self.request.user
        return Examen.objects.filter(
            Q(activo=True, publicado=True) &
            (Q(oposicion__in=user.oposiciones_acceso.all()) |
             Q(tema__in=user.temas_acceso.all()) |
             Q(oposicion__isnull=True, tema__isnull=True))
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.titulo
        
        if self.request.user.is_student():
            # Verificar intentos previos
            context['mis_intentos'] = IntentosExamen.objects.filter(
                estudiante=self.request.user,
                examen=self.object
            ).order_by('-fecha_inicio')
            
            context['puede_iniciar'] = self.object.esta_disponible and (
                context['mis_intentos'].count() < self.object.intentos_maximos
            )
            
            # Mejor intento
            mejor_intento = context['mis_intentos'].filter(completado=True).first()
            context['mejor_intento'] = mejor_intento
            
        return context


class IniciarExamenView(LoginRequiredMixin, DetailView):
    """Vista para iniciar un nuevo intento de examen"""
    model = Examen
    template_name = 'evaluaciones/iniciar_examen.html'

    def dispatch(self, request, *args, **kwargs):
        examen = self.get_object()
        
        # Verificaciones de seguridad
        if not examen.esta_disponible:
            messages.error(request, 'Este examen no está disponible en este momento.')
            return redirect('evaluaciones:examen_detail', pk=examen.pk)
        
        if request.user.is_student():
            intentos_previos = IntentosExamen.objects.filter(
                estudiante=request.user, examen=examen
            ).count()
            
            if intentos_previos >= examen.intentos_maximos:
                messages.error(request, 'Has alcanzado el número máximo de intentos para este examen.')
                return redirect('evaluaciones:examen_detail', pk=examen.pk)
        
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Crear nuevo intento de examen"""
        examen = self.get_object()
        
        # Crear nuevo intento
        intento = IntentosExamen.objects.create(
            estudiante=request.user,
            examen=examen,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Generar preguntas para el examen
        preguntas = examen.generar_preguntas()
        
        if len(preguntas) < examen.numero_preguntas:
            messages.warning(
                request, 
                f'Solo hay {len(preguntas)} preguntas disponibles de las {examen.numero_preguntas} solicitadas.'
            )
        
        # Asignar preguntas al intento
        for i, pregunta in enumerate(preguntas, 1):
            PreguntaExamen.objects.create(
                intento=intento,
                pregunta=pregunta,
                orden=i
            )
            
            # Crear registro de respuesta vacío
            RespuestaEstudiante.objects.create(
                intento=intento,
                pregunta=pregunta
            )
        
        messages.success(request, f'Examen iniciado. Tienes {examen.tiempo_limite} minutos.')
        return redirect('evaluaciones:realizar_examen', pk=intento.pk)

    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RealizarExamenView(LoginRequiredMixin, DetailView):
    """Vista principal para realizar el examen"""
    model = IntentosExamen
    template_name = 'evaluaciones/realizar_examen.html'
    context_object_name = 'intento'

    def get_queryset(self):
        return IntentosExamen.objects.filter(estudiante=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        intento = self.get_object()
        
        # Verificar que el intento no esté completado
        if intento.completado:
            messages.info(request, 'Este examen ya ha sido completado.')
            return redirect('evaluaciones:resultado_examen', pk=intento.pk)
        
        # Verificar tiempo límite
        if intento.tiempo_restante <= timedelta(0):
            messages.warning(request, 'El tiempo del examen ha expirado.')
            intento.finalizar_intento()
            return redirect('evaluaciones:resultado_examen', pk=intento.pk)
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Realizando: {self.object.examen.titulo}'
        
        # Obtener preguntas con respuestas mezcladas si es necesario
        preguntas_examen = self.object.preguntas_asignadas.all().select_related('pregunta')
        
        preguntas_data = []
        for pregunta_examen in preguntas_examen:
            pregunta = pregunta_examen.pregunta
            respuestas = list(pregunta.respuestas.all())
            
            if self.object.examen.respuestas_aleatorias:
                import random
                random.shuffle(respuestas)
            
            # Obtener respuesta del estudiante si existe
            respuesta_estudiante = RespuestaEstudiante.objects.filter(
                intento=self.object,
                pregunta=pregunta
            ).first()
            
            preguntas_data.append({
                'orden': pregunta_examen.orden,
                'pregunta': pregunta,
                'respuestas': respuestas,
                'respuesta_seleccionada': respuesta_estudiante.respuesta_seleccionada if respuesta_estudiante else None
            })
        
        context['preguntas'] = preguntas_data
        context['tiempo_restante'] = int(self.object.tiempo_restante.total_seconds())
        
        return context


@require_POST
@login_required
def guardar_respuesta(request):
    """Vista AJAX para guardar respuestas del estudiante"""
    try:
        data = json.loads(request.body)
        intento_id = data.get('intento_id')
        pregunta_id = data.get('pregunta_id')
        respuesta_id = data.get('respuesta_id')
        tiempo_respuesta = data.get('tiempo_respuesta')
        
        intento = get_object_or_404(IntentosExamen, 
                                  id=intento_id, 
                                  estudiante=request.user,
                                  completado=False)
        
        pregunta = get_object_or_404(BancoPregunta, id=pregunta_id)
        respuesta_seleccionada = None
        
        if respuesta_id:
            respuesta_seleccionada = get_object_or_404(RespuestaPregunta, 
                                                     id=respuesta_id, 
                                                     pregunta=pregunta)
        
        # Actualizar o crear respuesta del estudiante
        respuesta_estudiante, created = RespuestaEstudiante.objects.get_or_create(
            intento=intento,
            pregunta=pregunta,
            defaults={
                'respuesta_seleccionada': respuesta_seleccionada,
                'tiempo_respuesta': tiempo_respuesta
            }
        )
        
        if not created:
            respuesta_estudiante.respuesta_seleccionada = respuesta_seleccionada
            respuesta_estudiante.tiempo_respuesta = tiempo_respuesta
            respuesta_estudiante.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@login_required
def finalizar_examen(request):
    """Vista AJAX para finalizar el examen"""
    try:
        data = json.loads(request.body)
        intento_id = data.get('intento_id')
        
        intento = get_object_or_404(IntentosExamen, 
                                  id=intento_id, 
                                  estudiante=request.user,
                                  completado=False)
        
        intento.finalizar_intento()
        
        # Actualizar estadísticas del examen
        estadisticas, created = EstadisticasExamen.objects.get_or_create(
            examen=intento.examen
        )
        estadisticas.actualizar_estadisticas()
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('evaluaciones:resultado_examen', kwargs={'pk': intento.pk})
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


class ResultadoExamenView(LoginRequiredMixin, DetailView):
    """Vista para mostrar resultados del examen"""
    model = IntentosExamen
    template_name = 'evaluaciones/resultado_examen.html'
    context_object_name = 'intento'

    def get_queryset(self):
        return IntentosExamen.objects.filter(
            estudiante=self.request.user,
            completado=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Resultado: {self.object.examen.titulo}'
        
        # Detalles de respuestas si el examen permite revisión
        if self.object.examen.permitir_revision:
            respuestas = self.object.respuestas_dadas.select_related(
                'pregunta', 'respuesta_seleccionada'
            ).order_by('pregunta__preguntaexamen__orden')
            
            context['respuestas_detalle'] = respuestas
        
        # Estadísticas comparativas
        otros_intentos = IntentosExamen.objects.filter(
            examen=self.object.examen,
            completado=True
        ).exclude(id=self.object.id)
        
        if otros_intentos.exists():
            context['promedio_examen'] = otros_intentos.aggregate(
                Avg('porcentaje')
            )['porcentaje__avg']
            
            context['mejor_que_porcentaje'] = (
                otros_intentos.filter(porcentaje__lt=self.object.porcentaje).count() / 
                otros_intentos.count() * 100
            )
        
        return context


# ============================================================================
# VISTAS DE ADMINISTRACIÓN
# ============================================================================

class AdminExamenListView(AdminRequiredMixin, ListView):
    """Lista de exámenes para administración"""
    model = Examen
    template_name = 'evaluaciones/admin/examen_list.html'
    context_object_name = 'examenes'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Exámenes'
        return context


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = [
            'titulo', 'descripcion', 'tipo', 'oposicion', 'tema', 'categorias',
            'numero_preguntas', 'tiempo_limite', 'puntuacion_maxima', 
            'nota_minima_aprobado', 'preguntas_aleatorias', 'respuestas_aleatorias',
            'mostrar_resultados_inmediatos', 'permitir_revision', 'intentos_maximos',
            'fecha_inicio', 'fecha_fin', 'activo', 'publicado'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'oposicion': forms.Select(attrs={'class': 'form-control'}),
            'tema': forms.Select(attrs={'class': 'form-control'}),
            'categorias': forms.CheckboxSelectMultiple(),
            'numero_preguntas': forms.NumberInput(attrs={'class': 'form-control'}),
            'tiempo_limite': forms.NumberInput(attrs={'class': 'form-control'}),
            'puntuacion_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'nota_minima_aprobado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'intentos_maximos': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oposicion'].required = False
        self.fields['tema'].required = False
        
        # Configurar checkboxes
        for field_name in ['preguntas_aleatorias', 'respuestas_aleatorias', 
                          'mostrar_resultados_inmediatos', 'permitir_revision', 
                          'activo', 'publicado']:
            self.fields[field_name].widget = forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })


class AdminExamenCreateView(AdminRequiredMixin, CreateView):
    """Crear nuevo examen"""
    model = Examen
    form_class = ExamenForm
    template_name = 'evaluaciones/admin/examen_form.html'
    success_url = reverse_lazy('evaluaciones:admin_examen_list')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Examen creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Examen'
        context['form_title'] = 'Nuevo Examen'
        return context


class AdminExamenUpdateView(AdminRequiredMixin, UpdateView):
    """Editar examen existente"""
    model = Examen
    form_class = ExamenForm
    template_name = 'evaluaciones/admin/examen_form.html'
    success_url = reverse_lazy('evaluaciones:admin_examen_list')

    def form_valid(self, form):
        messages.success(self.request, 'Examen actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar {self.object.titulo}'
        context['form_title'] = 'Editar Examen'
        return context


class AdminExamenDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar examen"""
    model = Examen
    template_name = 'evaluaciones/admin/examen_confirm_delete.html'
    success_url = reverse_lazy('evaluaciones:admin_examen_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Examen eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# GESTIÓN DEL BANCO DE PREGUNTAS
# ============================================================================

class BancoPreguntaListView(AdminRequiredMixin, ListView):
    """Lista del banco de preguntas"""
    model = BancoPregunta
    template_name = 'evaluaciones/admin/banco_pregunta_list.html'
    context_object_name = 'preguntas'
    paginate_by = 20

    def get_queryset(self):
        queryset = BancoPregunta.objects.select_related('categoria', 'creada_por')
        
        # Filtros
        categoria = self.request.GET.get('categoria')
        dificultad = self.request.GET.get('dificultad')
        buscar = self.request.GET.get('q')
        
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if dificultad:
            queryset = queryset.filter(dificultad=dificultad)
        if buscar:
            queryset = queryset.filter(
                Q(enunciado__icontains=buscar) | 
                Q(explicacion__icontains=buscar)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Banco de Preguntas'
        context['categorias'] = Categoria.objects.filter(activa=True)
        context['dificultades'] = BancoPregunta._meta.get_field('dificultad').choices
        return context


# ============================================================================
# REPORTES Y ESTADÍSTICAS
# ============================================================================

class EstadisticasExamenView(AdminRequiredMixin, DetailView):
    """Estadísticas detalladas de un examen"""
    model = Examen
    template_name = 'evaluaciones/admin/estadisticas_examen.html'
    context_object_name = 'examen'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Estadísticas: {self.object.titulo}'
        
        # Obtener o crear estadísticas
        estadisticas, created = EstadisticasExamen.objects.get_or_create(
            examen=self.object
        )
        if created or (timezone.now() - estadisticas.updated_at).days > 0:
            estadisticas.actualizar_estadisticas()
        
        context['estadisticas'] = estadisticas
        
        # Intentos recientes
        context['intentos_recientes'] = self.object.intentos.filter(
            completado=True
        ).select_related('estudiante').order_by('-fecha_fin')[:10]
        
        # Gráfico de distribución de puntuaciones
        intentos = self.object.intentos.filter(completado=True)
        rangos = [
            ('0-20', intentos.filter(porcentaje__lt=20).count()),
            ('20-40', intentos.filter(porcentaje__gte=20, porcentaje__lt=40).count()),
            ('40-60', intentos.filter(porcentaje__gte=40, porcentaje__lt=60).count()),
            ('60-80', intentos.filter(porcentaje__gte=60, porcentaje__lt=80).count()),
            ('80-100', intentos.filter(porcentaje__gte=80).count()),
        ]
        context['distribucion_puntuaciones'] = rangos
        
        return context