# core/views.py - ACTUALIZADO con gestión de relación Oposicion-Tema

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Prefetch
from django import forms
from .models import Oposicion, Tema, TemaOposicion, Apartado, Pregunta, Respuesta, ExamenTest, ExamenTestResultado, RespuestaExamenTest
from accounts.models import CustomUser
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.db import transaction
import random


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de administrador"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return super().handle_no_permission()


class HomeView(TemplateView):
    """Vista de la página principal - redirige directamente al login o dashboard"""
    
    def dispatch(self, request, *args, **kwargs):
        # Si el usuario está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        else:
            # Si no está autenticado, redirigir al login
            return redirect('accounts:login')
        
        # Este código nunca se ejecutará, pero lo dejamos por consistencia
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del usuario"""
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['title'] = 'Dashboard'
        context['user_type'] = user.get_user_type_display()
        
        if user.is_student():
            # Obtener oposiciones con sus temas
            mis_oposiciones = user.oposiciones_acceso.prefetch_related('temas')[:5]
            context['mis_oposiciones'] = mis_oposiciones
            context['mis_temas'] = user.temas_acceso.prefetch_related('oposiciones')[:5]
            context['total_oposiciones'] = user.oposiciones_acceso.count()
            context['total_temas'] = user.temas_acceso.count()
            
            # Estadísticas adicionales
            total_temas_oposiciones = sum([op.temas.count() for op in mis_oposiciones])
            context['total_temas_en_oposiciones'] = total_temas_oposiciones
            
            # Información del rango y ranking
            context['rango_info'] = user.get_rango_firefighter()
            
            # Obtener estadísticas de actividad
            activity_stats = user.get_activity_stats()
            context['activity_stats'] = activity_stats
            
            if activity_stats:
                context['activity_level'] = activity_stats.get_activity_level()
                context['streak_milestone'] = activity_stats.get_streak_milestone_message()
                
                # Verificar si la racha se rompió
                if activity_stats.check_streak_broken():
                    messages.warning(request, 'Tu racha de estudio se ha roto. ¡Realiza un examen hoy para comenzar una nueva!')
            
            # Calcular posición en ranking mejorado
            try:
                estudiantes = CustomUser.objects.filter(user_type='student')
                ranking_scores = []
                
                for estudiante in estudiantes:
                    score = estudiante.get_enhanced_ranking_score()
                    if score > 0:  # Solo incluir estudiantes con exámenes
                        ranking_scores.append((estudiante, score))
                
                # Ordenar por puntaje mejorado
                ranking_scores.sort(key=lambda x: -x[1])
                
                # Buscar posición del usuario actual
                mi_posicion = None
                for idx, (estudiante, score) in enumerate(ranking_scores):
                    if estudiante == user:
                        mi_posicion = idx + 1
                        break
                
                context['mi_posicion_ranking'] = mi_posicion
                context['total_estudiantes_ranking'] = len(ranking_scores)
                context['mi_score_mejorado'] = user.get_enhanced_ranking_score()
            except Exception as e:
                context['mi_posicion_ranking'] = None
                context['total_estudiantes_ranking'] = 0
                context['mi_score_mejorado'] = 0
            
        elif user.is_admin():
            context['total_oposiciones'] = Oposicion.objects.count()
            context['total_temas'] = Tema.objects.count()
            context['total_estudiantes'] = CustomUser.objects.filter(user_type='student').count()
            context['oposiciones_recientes'] = Oposicion.objects.prefetch_related('temas').order_by('-created_at')[:5]
            context['temas_recientes'] = Tema.objects.prefetch_related('oposiciones').order_by('-created_at')[:5]
            
            # Estadísticas adicionales para admin
            from core.models import ArchivoOposicion, ArchivoTema
            context['total_archivos_oposiciones'] = ArchivoOposicion.objects.count()
            context['total_archivos_temas'] = ArchivoTema.objects.count()
            
            # Accesos rápidos
            context['accesos_rapidos'] = [
                {'name': 'Crear Oposición', 'url': 'core:admin_oposicion_create', 'icon': 'bi-plus-circle'},
                {'name': 'Crear Tema', 'url': 'core:admin_tema_create', 'icon': 'bi-journal-plus'},
                {'name': 'Gestionar Usuarios', 'url': 'core:admin_user_list', 'icon': 'bi-people'},
                {'name': 'Ver Oposiciones', 'url': 'core:admin_oposicion_list', 'icon': 'bi-fire'},
                {'name': 'Ver Temas', 'url': 'core:admin_tema_list', 'icon': 'bi-book'},
            ]
            
        return context


# Vistas para Estudiantes
class OposicionListView(LoginRequiredMixin, ListView):
    """Lista de oposiciones para estudiantes"""
    model = Oposicion
    template_name = 'core/oposicion_list.html'
    context_object_name = 'oposiciones'
    paginate_by = 12

    def get_queryset(self):
        queryset = Oposicion.objects.prefetch_related('temas', 'alumnos_con_acceso')
        
        if self.request.user.is_admin():
            return queryset.all()
        return queryset.filter(alumnos_con_acceso=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Oposiciones'
        return context


class OposicionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de oposición con sus temas"""
    model = Oposicion
    template_name = 'core/oposicion_detail.html'
    context_object_name = 'oposicion'

    def get_queryset(self):
        queryset = Oposicion.objects.prefetch_related(
            'temas__archivos',
            'archivos',
            'alumnos_con_acceso'
        )
        
        if self.request.user.is_admin():
            return queryset.all()
        return queryset.filter(alumnos_con_acceso=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.nombre
        
        # Obtener temas ordenados de la oposición
        temas_oposicion = self.object.temas.prefetch_related('archivos').order_by('orden', 'nombre')
        
        # Añadir información de progreso a cada tema para estudiantes
        if self.request.user.is_student():
            temas_con_progreso = []
            for tema in temas_oposicion:
                # Aquí puedes calcular el progreso del estudiante en cada tema
                tema.progreso = {
                    'completado': False,  # Implementar lógica de progreso
                    'porcentaje': 0,
                }
                temas_con_progreso.append(tema)
            context['temas'] = temas_con_progreso
        else:
            context['temas'] = temas_oposicion
        
        return context


class TemaListView(LoginRequiredMixin, ListView):
    """Lista de temas para estudiantes"""
    model = Tema
    template_name = 'core/tema_list.html'
    context_object_name = 'temas'
    paginate_by = 12

    def get_queryset(self):
        queryset = Tema.objects.prefetch_related('oposiciones', 'alumnos_con_acceso')
        
        if self.request.user.is_admin():
            return queryset.all()
        return queryset.filter(alumnos_con_acceso=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Temas'
        return context


class TemaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de tema con sus oposiciones"""
    model = Tema
    template_name = 'core/tema_detail.html'
    context_object_name = 'tema'

    def get_queryset(self):
        queryset = Tema.objects.prefetch_related(
            'oposiciones',
            'archivos',
            'alumnos_con_acceso'
        )
        
        if self.request.user.is_admin():
            return queryset.all()
        return queryset.filter(alumnos_con_acceso=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.nombre
        
        # Obtener oposiciones relacionadas según el tipo de usuario
        if self.request.user.is_admin():
            # Los administradores ven todas las oposiciones
            context['oposiciones_relacionadas'] = self.object.oposiciones.all()
        else:
            # Los estudiantes solo ven las oposiciones a las que tienen acceso
            context['oposiciones_relacionadas'] = self.object.oposiciones.filter(
                alumnos_con_acceso=self.request.user
            )
        
        return context


# Formularios actualizados
class OposicionCreateForm(forms.ModelForm):
    """Formulario para crear oposiciones"""
    class Meta:
        model = Oposicion
        fields = ['nombre', 'descripcion', 'fecha_convocatoria', 'alumnos_con_acceso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fecha_convocatoria': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'alumnos_con_acceso': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumnos_con_acceso'].queryset = CustomUser.objects.filter(user_type='student')
        self.fields['fecha_convocatoria'].help_text = "Fecha de la convocatoria oficial"


class OposicionUpdateForm(forms.ModelForm):
    """Formulario para editar oposiciones"""
    class Meta:
        model = Oposicion
        fields = ['nombre', 'descripcion', 'fecha_convocatoria', 'alumnos_con_acceso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fecha_convocatoria': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'readonly': True,
                'style': 'background-color: #f8f9fa; cursor: not-allowed;'
            }),
            'alumnos_con_acceso': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumnos_con_acceso'].queryset = CustomUser.objects.filter(user_type='student')
        self.fields['fecha_convocatoria'].help_text = "La fecha de convocatoria no puede modificarse una vez creada"
        self.fields['fecha_convocatoria'].disabled = True


class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nombre', 'descripcion', 'oposiciones', 'alumnos_con_acceso', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oposiciones': forms.CheckboxSelectMultiple(),
            'alumnos_con_acceso': forms.CheckboxSelectMultiple(),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumnos_con_acceso'].queryset = CustomUser.objects.filter(user_type='student')
        self.fields['oposiciones'].queryset = Oposicion.objects.all()


# Formulario para gestionar temas en una oposición específica
class TemasOposicionForm(forms.Form):
    """Formulario para añadir/quitar temas de una oposición"""
    temas = forms.ModelMultipleChoiceField(
        queryset=Tema.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text="Selecciona los temas que pertenecen a esta oposición"
    )
    
    def __init__(self, *args, **kwargs):
        oposicion = kwargs.pop('oposicion', None)
        super().__init__(*args, **kwargs)
        
        if oposicion:
            # Marcar temas actuales como seleccionados
            self.fields['temas'].initial = oposicion.temas.all()


# Vistas para Administradores - Oposiciones
class AdminOposicionListView(AdminRequiredMixin, ListView):
    """Lista de oposiciones para admin"""
    model = Oposicion
    template_name = 'core/admin/oposicion_list.html'
    context_object_name = 'oposiciones'
    paginate_by = 15

    def get_queryset(self):
        return Oposicion.objects.prefetch_related('temas', 'alumnos_con_acceso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Oposiciones'
        return context


class AdminOposicionCreateView(AdminRequiredMixin, CreateView):
    """Crear oposición"""
    model = Oposicion
    form_class = OposicionCreateForm
    template_name = 'core/admin/oposicion_form.html'
    success_url = reverse_lazy('core:admin_oposicion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Oposición'
        context['form_title'] = 'Nueva Oposición'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Oposición creada exitosamente.')
        return super().form_valid(form)


class AdminOposicionUpdateView(AdminRequiredMixin, UpdateView):
    """Editar oposición"""
    model = Oposicion
    form_class = OposicionUpdateForm
    template_name = 'core/admin/oposicion_form.html'
    success_url = reverse_lazy('core:admin_oposicion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar {self.object.nombre}'
        context['form_title'] = 'Editar Oposición'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Oposición actualizada exitosamente.')
        return super().form_valid(form)


class AdminOposicionDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar oposición"""
    model = Oposicion
    template_name = 'core/admin/oposicion_confirm_delete.html'
    success_url = reverse_lazy('core:admin_oposicion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar {self.object.nombre}'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Oposición eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# Vista para gestionar temas de una oposición
class AdminOposicionTemasView(AdminRequiredMixin, UpdateView):
    """Gestionar temas de una oposición"""
    model = Oposicion
    template_name = 'core/admin/oposicion_temas.html'
    fields = []  # No usamos fields porque usamos form personalizado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Gestionar Temas - {self.object.nombre}'
        context['form'] = TemasOposicionForm(oposicion=self.object)
        context['temas_actuales'] = self.object.temas.all()
        context['todos_los_temas'] = Tema.objects.all()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TemasOposicionForm(request.POST, oposicion=self.object)
        
        if form.is_valid():
            # Actualizar relación many-to-many
            temas_seleccionados = form.cleaned_data['temas']
            self.object.temas.set(temas_seleccionados)
            
            messages.success(request, f'Temas de "{self.object.nombre}" actualizados correctamente.')
            return redirect('core:admin_oposicion_list')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# Vistas para Administradores - Temas
class AdminTemaListView(AdminRequiredMixin, ListView):
    model = Tema
    template_name = 'core/admin/tema_list.html'
    context_object_name = 'temas'
    paginate_by = 15

    def get_queryset(self):
        return Tema.objects.prefetch_related('oposiciones', 'alumnos_con_acceso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Temas'
        return context


class AdminTemaCreateView(AdminRequiredMixin, CreateView):
    model = Tema
    form_class = TemaForm
    template_name = 'core/admin/tema_form.html'
    success_url = reverse_lazy('core:admin_tema_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Tema'
        context['form_title'] = 'Nuevo Tema'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tema creado exitosamente.')
        return super().form_valid(form)


class AdminTemaUpdateView(AdminRequiredMixin, UpdateView):
    model = Tema
    form_class = TemaForm
    template_name = 'core/admin/tema_form.html'
    success_url = reverse_lazy('core:admin_tema_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar {self.object.nombre}'
        context['form_title'] = 'Editar Tema'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tema actualizado exitosamente.')
        return super().form_valid(form)


class AdminTemaDeleteView(AdminRequiredMixin, DeleteView):
    model = Tema
    template_name = 'core/admin/tema_confirm_delete.html'
    success_url = reverse_lazy('core:admin_tema_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar {self.object.nombre}'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tema eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Resto de vistas de usuario (sin cambios)...
class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
        self.fields['is_active'].label = 'Usuario Activo'
        
        if self.instance and self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'user_type', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = True
        self.fields['user_type'].initial = 'student'
        
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
        self.fields['is_active'].label = 'Usuario Activo'
        
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUserListView(AdminRequiredMixin, ListView):
    """Lista de usuarios para admin"""
    model = CustomUser
    template_name = 'core/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='student').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestión de Usuarios'
        return context


class AdminUserCreateView(AdminRequiredMixin, CreateView):
    """Crear usuario"""
    model = CustomUser
    form_class = UserCreateForm
    template_name = 'core/admin/user_form.html'
    success_url = reverse_lazy('core:admin_user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Usuario'
        context['form_title'] = 'Nuevo Usuario'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)


class AdminUserDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar usuario"""
    model = CustomUser
    template_name = 'core/admin/user_confirm_delete.html'
    success_url = reverse_lazy('core:admin_user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Usuario: {self.object.username}'
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
            return redirect('core:admin_user_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Usuario "{self.object.username}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class AdminUserUpdateView(AdminRequiredMixin, UpdateView):
    """Editar usuario"""
    model = CustomUser
    form_class = UserEditForm
    template_name = 'core/admin/user_form.html'
    success_url = reverse_lazy('core:admin_user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Usuario: {self.object.username}'
        context['form_title'] = 'Editar Usuario'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)


# =================== VISTAS PARA APARTADOS ===================

class ApartadoForm(forms.ModelForm):
    """Formulario para crear/editar apartados"""
    class Meta:
        model = Apartado
        fields = ['nombre', 'descripcion', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False
        self.fields['orden'].help_text = "Orden de aparición en el tema (números más bajos aparecen primero)"


class AdminApartadoListView(AdminRequiredMixin, ListView):
    """Lista de apartados para un tema específico"""
    model = Apartado
    template_name = 'core/admin/apartado_list.html'
    context_object_name = 'apartados'
    paginate_by = 20
    
    def get_queryset(self):
        self.tema = get_object_or_404(Tema, pk=self.kwargs['tema_id'])
        return Apartado.objects.filter(tema=self.tema).order_by('orden', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        context['title'] = f'Apartados de {self.tema.nombre}'
        return context


class AdminApartadoCreateView(AdminRequiredMixin, CreateView):
    """Crear apartado para un tema específico"""
    model = Apartado
    form_class = ApartadoForm
    template_name = 'core/admin/apartado_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=self.kwargs['tema_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        context['title'] = f'Crear Apartado para {self.tema.nombre}'
        context['form_title'] = 'Nuevo Apartado'
        return context
    
    def form_valid(self, form):
        form.instance.tema = self.tema
        messages.success(self.request, f'Apartado "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:admin_apartado_list', kwargs={'tema_id': self.tema.id})


class AdminApartadoUpdateView(AdminRequiredMixin, UpdateView):
    """Editar apartado"""
    model = Apartado
    form_class = ApartadoForm
    template_name = 'core/admin/apartado_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.object.tema
        context['title'] = f'Editar Apartado: {self.object.nombre}'
        context['form_title'] = 'Editar Apartado'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Apartado "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:admin_apartado_list', kwargs={'tema_id': self.object.tema.id})


class AdminApartadoDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar apartado"""
    model = Apartado
    template_name = 'core/admin/apartado_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.object.tema
        context['title'] = f'Eliminar Apartado: {self.object.nombre}'
        return context
    
    def get_success_url(self):
        return reverse_lazy('core:admin_apartado_list', kwargs={'tema_id': self.object.tema.id})
    
    def delete(self, request, *args, **kwargs):
        apartado_nombre = self.get_object().nombre
        messages.success(request, f'Apartado "{apartado_nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# =================== VISTAS PARA PREGUNTAS ===================

# Formulario para crear/editar preguntas con respuestas inline
class RespuestaForm(forms.ModelForm):
    """Formulario para respuestas individuales"""
    class Meta:
        model = Respuesta
        fields = ['texto', 'es_correcta', 'explicacion']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'explicacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['explicacion'].required = False


# Formset para manejar múltiples respuestas
RespuestaFormSet = forms.inlineformset_factory(
    Pregunta,
    Respuesta,
    form=RespuestaForm,
    extra=4,
    min_num=2,
    max_num=6,
    can_delete=True,
    can_order=False  # Sin orden ya que se mostrarán aleatoriamente
)


class PreguntaForm(forms.ModelForm):
    """Formulario para crear/editar preguntas"""
    class Meta:
        model = Pregunta
        fields = ['enunciado', 'texto_aclaratorio', 'activa']
        widgets = {
            'enunciado': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'texto_aclaratorio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['texto_aclaratorio'].required = False
        self.fields['activa'].initial = True


class AdminPreguntaListView(AdminRequiredMixin, ListView):
    """Lista de preguntas para un apartado específico"""
    model = Pregunta
    template_name = 'core/admin/pregunta_list.html'
    context_object_name = 'preguntas'
    paginate_by = 20
    
    def get_queryset(self):
        self.apartado = get_object_or_404(Apartado, pk=self.kwargs['apartado_id'])
        return Pregunta.objects.filter(apartado=self.apartado).prefetch_related('respuestas').order_by('created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartado'] = self.apartado
        context['tema'] = self.apartado.tema
        context['title'] = f'Preguntas de {self.apartado.nombre}'
        return context


class AdminPreguntaCreateView(AdminRequiredMixin, CreateView):
    """Crear pregunta para un apartado específico"""
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'core/admin/pregunta_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.apartado = get_object_or_404(Apartado, pk=self.kwargs['apartado_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartado'] = self.apartado
        context['tema'] = self.apartado.tema
        context['title'] = f'Crear Pregunta para {self.apartado.nombre}'
        context['form_title'] = 'Nueva Pregunta'
        
        if self.request.POST:
            context['respuesta_formset'] = RespuestaFormSet(self.request.POST)
        else:
            context['respuesta_formset'] = RespuestaFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        respuesta_formset = context['respuesta_formset']
        
        if respuesta_formset.is_valid():
            form.instance.apartado = self.apartado
            self.object = form.save()
            respuesta_formset.instance = self.object
            respuesta_formset.save()
            
            # Verificar que haya al menos una respuesta correcta
            if not self.object.respuestas.filter(es_correcta=True).exists():
                messages.error(self.request, 'Debe haber al menos una respuesta correcta.')
                return self.form_invalid(form)
            
            messages.success(self.request, f'Pregunta creada exitosamente.')
            return redirect(self.get_success_url())
        else:
            # Debug: mostrar errores del formset
            for i, form_errors in enumerate(respuesta_formset.errors):
                if form_errors:
                    messages.error(self.request, f'Error en respuesta {i+1}: {form_errors}')
            if respuesta_formset.non_form_errors():
                messages.error(self.request, f'Errores del formset: {respuesta_formset.non_form_errors()}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:admin_pregunta_list', kwargs={'apartado_id': self.apartado.id})


class AdminPreguntaUpdateView(AdminRequiredMixin, UpdateView):
    """Editar pregunta"""
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'core/admin/pregunta_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartado'] = self.object.apartado
        context['tema'] = self.object.apartado.tema
        context['title'] = f'Editar Pregunta'
        context['form_title'] = 'Editar Pregunta'
        
        if self.request.POST:
            context['respuesta_formset'] = RespuestaFormSet(self.request.POST, instance=self.object)
        else:
            context['respuesta_formset'] = RespuestaFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        respuesta_formset = context['respuesta_formset']
        
        if respuesta_formset.is_valid():
            self.object = form.save()
            respuesta_formset.instance = self.object
            respuesta_formset.save()
            
            # Verificar que haya al menos una respuesta correcta
            if not self.object.respuestas.filter(es_correcta=True).exists():
                messages.error(self.request, 'Debe haber al menos una respuesta correcta.')
                return self.form_invalid(form)
            
            messages.success(self.request, f'Pregunta actualizada exitosamente.')
            return redirect(self.get_success_url())
        else:
            # Debug: mostrar errores del formset
            for i, form_errors in enumerate(respuesta_formset.errors):
                if form_errors:
                    messages.error(self.request, f'Error en respuesta {i+1}: {form_errors}')
            if respuesta_formset.non_form_errors():
                messages.error(self.request, f'Errores del formset: {respuesta_formset.non_form_errors()}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:admin_pregunta_list', kwargs={'apartado_id': self.object.apartado.id})


class AdminPreguntaDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar pregunta"""
    model = Pregunta
    template_name = 'core/admin/pregunta_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartado'] = self.object.apartado
        context['tema'] = self.object.apartado.tema
        context['title'] = f'Eliminar Pregunta'
        return context
    
    def get_success_url(self):
        return reverse_lazy('core:admin_pregunta_list', kwargs={'apartado_id': self.object.apartado.id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Pregunta eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VISTAS DEL SISTEMA DE EXÁMENES
# ============================================================================

class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de estudiante (o admin)"""
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_student() or self.request.user.is_admin())

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:dashboard')


class ExamenTestListView(LoginRequiredMixin, ListView):
    """Lista de exámenes del estudiante"""
    model = ExamenTest
    template_name = 'core/examen/examen_list.html'
    context_object_name = 'examenes'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_admin():
            return ExamenTest.objects.all().order_by('-created_at')
        return ExamenTest.objects.filter(estudiante=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Exámenes'
        return context


class ExamenTestConfigView(LoginRequiredMixin, TemplateView):
    """Vista para configurar un nuevo examen"""
    template_name = 'core/examen/examen_config.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Configurar Examen'
        
        # Obtener temas disponibles para el usuario
        if self.request.user.is_admin():
            context['temas_disponibles'] = Tema.objects.all().prefetch_related('apartados')
        else:
            context['temas_disponibles'] = Tema.objects.filter(
                alumnos_con_acceso=self.request.user
            ).prefetch_related('apartados')
        
        return context

    def post(self, request, *args, **kwargs):
        """Crear nuevo examen con la configuración seleccionada"""
        try:
            # Obtener datos del formulario
            tipo = request.POST.get('tipo')
            numero_preguntas = int(request.POST.get('numero_preguntas', 10))
            tiempo_por_pregunta = int(request.POST.get('tiempo_por_pregunta', 0))
            tipo_aclaracion = request.POST.get('tipo_aclaracion', 'inmediata')  # Valor por defecto
            temas_ids = request.POST.getlist('temas')
            apartados_ids = request.POST.getlist('apartados')
            
            # Validar tipo_aclaracion
            if not tipo_aclaracion or tipo_aclaracion not in ['inmediata', 'final']:
                tipo_aclaracion = 'final' if tipo == 'examen' else 'inmediata'

            # Validaciones
            if numero_preguntas < 10:
                messages.error(request, 'El número mínimo de preguntas es 10.')
                return redirect('core:examen_config')

            if not temas_ids:
                messages.error(request, 'Debes seleccionar al menos un tema.')
                return redirect('core:examen_config')

            # Generar nombre automáticamente
            if request.user.is_admin():
                temas = Tema.objects.filter(id__in=temas_ids)
            else:
                temas = Tema.objects.filter(id__in=temas_ids, alumnos_con_acceso=request.user)
            
            if temas.count() == 1:
                nombre = f"Examen de {temas.first().nombre}"
            else:
                nombre = f"Examen de {temas.count()} temas"
            
            # Añadir tipo al nombre
            if tipo == 'examen':
                nombre += " (Examen)"
            
            # Crear examen
            examen = ExamenTest.objects.create(
                estudiante=request.user,
                nombre=nombre,
                tipo=tipo,
                numero_preguntas=numero_preguntas,
                tiempo_por_pregunta=tiempo_por_pregunta,
                tipo_aclaracion=tipo_aclaracion,
                fecha_inicio=timezone.now()
            )

            # Asociar temas (ya fueron cargados arriba)
            examen.temas_seleccionados.set(temas)

            # Asociar apartados si se seleccionaron
            if apartados_ids:
                apartados = Apartado.objects.filter(id__in=apartados_ids, tema__in=temas)
                examen.apartados_seleccionados.set(apartados)

            messages.success(request, 'Examen configurado exitosamente.')
            return redirect('core:examen_ejecutar', examen_id=examen.id)

        except Exception as e:
            messages.error(request, f'Error al configurar el examen: {str(e)}')
            return redirect('core:examen_config')


class ExamenTestEjecutarView(LoginRequiredMixin, DetailView):
    """Vista para ejecutar un examen"""
    model = ExamenTest
    template_name = 'core/examen/examen_ejecutar.html'
    context_object_name = 'examen'
    pk_url_kwarg = 'examen_id'

    def get_object(self):
        examen = super().get_object()
        if examen.estudiante != self.request.user and not self.request.user.is_admin():
            raise Http404("Examen no encontrado")
        return examen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Examen: {self.object.nombre}'
        
        # Obtener preguntas para el examen
        preguntas = self.get_preguntas_examen()
        context['preguntas'] = preguntas
        context['total_preguntas'] = len(preguntas)
        
        # Convertir preguntas a JSON para JavaScript
        import json
        from django.utils.html import escape
        preguntas_json = []
        for pregunta in preguntas:
            pregunta_dict = {
                'id': pregunta.id,
                'enunciado': escape(pregunta.enunciado),
                'textoAclaratorio': escape(pregunta.texto_aclaratorio or ''),
                'respuestas': []
            }
            for respuesta in pregunta.respuestas.all():
                pregunta_dict['respuestas'].append({
                    'id': respuesta.id,
                    'texto': escape(respuesta.texto),
                    'esCorrecta': respuesta.es_correcta,
                    'explicacion': escape(respuesta.explicacion or '')
                })
            preguntas_json.append(pregunta_dict)
        
        context['preguntas_json'] = json.dumps(preguntas_json, ensure_ascii=False, indent=2)
        
        return context

    def get_preguntas_examen(self):
        """Obtener preguntas aleatorias para el examen"""
        examen = self.object
        
        # Obtener preguntas disponibles
        if examen.apartados_seleccionados.exists():
            # Si hay apartados específicos seleccionados
            preguntas_disponibles = Pregunta.objects.filter(
                apartado__in=examen.apartados_seleccionados.all(),
                activa=True
            ).select_related('apartado__tema').prefetch_related('respuestas')
        else:
            # Si no hay apartados específicos, usar todos los de los temas
            preguntas_disponibles = Pregunta.objects.filter(
                apartado__tema__in=examen.temas_seleccionados.all(),
                activa=True
            ).select_related('apartado__tema').prefetch_related('respuestas')
        
        # Obtener preguntas aleatorias
        preguntas_list = list(preguntas_disponibles)
        if len(preguntas_list) == 0:
            messages.error(
                self.request,
                'No hay preguntas disponibles para los temas seleccionados.'
            )
            return []
            
        if len(preguntas_list) < examen.numero_preguntas:
            messages.warning(
                self.request, 
                f'Solo hay {len(preguntas_list)} preguntas disponibles. Se ajustará el número de preguntas.'
            )
            
        # Seleccionar preguntas aleatorias
        num_preguntas = min(examen.numero_preguntas, len(preguntas_list))
        if num_preguntas == 0:
            return []
            
        preguntas_seleccionadas = random.sample(preguntas_list, num_preguntas)
        
        # Verificar que las preguntas tengan respuestas
        preguntas_con_respuestas = []
        for pregunta in preguntas_seleccionadas:
            if pregunta.respuestas.exists():
                preguntas_con_respuestas.append(pregunta)
        
        if len(preguntas_con_respuestas) < len(preguntas_seleccionadas):
            messages.warning(
                self.request,
                f'Algunas preguntas no tienen respuestas y fueron omitidas.'
            )
            
        return preguntas_con_respuestas


class ExamenTestRespuestaView(LoginRequiredMixin, TemplateView):
    """Vista para procesar respuestas del examen"""
    
    def post(self, request, *args, **kwargs):
        """Procesar respuesta de una pregunta"""
        try:
            examen_id = kwargs.get('examen_id')
            examen = get_object_or_404(ExamenTest, id=examen_id)
            if examen.estudiante != request.user and not request.user.is_admin():
                return JsonResponse({'success': False, 'error': 'No tienes permisos para este examen'})
            
            pregunta_id = request.POST.get('pregunta_id')
            respuesta_id = request.POST.get('respuesta_id')
            tiempo_empleado = int(request.POST.get('tiempo_empleado', 0))
            orden_pregunta = int(request.POST.get('orden_pregunta', 1))
            timeout = request.POST.get('timeout', 'false') == 'true'
            penalizada_por_pausa = request.POST.get('penalizada_por_pausa', 'false') == 'true'
            
            pregunta = get_object_or_404(Pregunta, id=pregunta_id)
            respuesta_seleccionada = None
            es_correcta = False
            
            if respuesta_id and not timeout:
                respuesta_seleccionada = get_object_or_404(Respuesta, id=respuesta_id)
                es_correcta = respuesta_seleccionada.es_correcta
            
            # Guardar respuesta
            respuesta_examen, created = RespuestaExamenTest.objects.get_or_create(
                examen=examen,
                pregunta=pregunta,
                defaults={
                    'respuesta_seleccionada': respuesta_seleccionada,
                    'es_correcta': es_correcta,
                    'tiempo_empleado_segundos': tiempo_empleado,
                    'orden_pregunta': orden_pregunta,
                    'timeout': timeout,
                    'penalizada_por_pausa': penalizada_por_pausa
                }
            )
            
            # Preparar respuesta JSON
            response_data = {
                'success': True,
                'es_correcta': es_correcta,
                'respuesta_correcta_id': pregunta.respuesta_correcta.id if pregunta.respuesta_correcta else None,
                'timeout': timeout
            }
            
            # Añadir aclaración si es modo inmediato
            if examen.tipo_aclaracion == 'inmediata':
                response_data['texto_aclaratorio'] = pregunta.texto_aclaratorio
                if respuesta_seleccionada:
                    response_data['explicacion_respuesta'] = respuesta_seleccionada.explicacion
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class ExamenTestFinalizarView(LoginRequiredMixin, TemplateView):
    """Vista para finalizar un examen"""
    
    def post(self, request, *args, **kwargs):
        """Finalizar examen y generar resultado"""
        try:
            examen_id = kwargs.get('examen_id')
            examen = get_object_or_404(ExamenTest, id=examen_id)
            if examen.estudiante != request.user and not request.user.is_admin():
                return JsonResponse({'success': False, 'error': 'No tienes permisos para este examen'})
            
            # Verificar si el examen ya está completado
            if examen.completado:
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse_lazy('core:examen_resultado', kwargs={'examen_id': examen.id})
                })
            
            # Marcar examen como completado
            examen.completado = True
            examen.fecha_fin = timezone.now()
            examen.save()
            
            # Calcular resultados
            respuestas = examen.respuestas_examen.all()
            preguntas_correctas = respuestas.filter(es_correcta=True).count()
            preguntas_incorrectas = respuestas.filter(es_correcta=False, timeout=False).count()
            preguntas_sin_responder = respuestas.filter(timeout=True).count()
            
            tiempo_total = sum([r.tiempo_empleado_segundos for r in respuestas])
            porcentaje_acierto = (preguntas_correctas / len(respuestas)) * 100 if respuestas else 0
            
            # Crear o actualizar resultado
            resultado, created = ExamenTestResultado.objects.get_or_create(
                examen=examen,
                defaults={
                    'estudiante': examen.estudiante,
                    'nombre_examen': examen.nombre,
                    'fecha_completado': examen.fecha_fin,
                    'tipo_examen': examen.tipo,
                    'puntuacion_total': preguntas_correctas,
                    'puntuacion_maxima': len(respuestas),
                    'porcentaje_acierto': porcentaje_acierto,
                    'tiempo_total_segundos': tiempo_total,
                    'preguntas_correctas': preguntas_correctas,
                    'preguntas_incorrectas': preguntas_incorrectas,
                    'preguntas_sin_responder': preguntas_sin_responder
                }
            )
            
            # Si el resultado ya existía, actualizarlo
            if not created:
                resultado.estudiante = examen.estudiante
                resultado.nombre_examen = examen.nombre
                resultado.fecha_completado = examen.fecha_fin
                resultado.tipo_examen = examen.tipo
                resultado.puntuacion_total = preguntas_correctas
                resultado.puntuacion_maxima = len(respuestas)
                resultado.porcentaje_acierto = porcentaje_acierto
                resultado.tiempo_total_segundos = tiempo_total
                resultado.preguntas_correctas = preguntas_correctas
                resultado.preguntas_incorrectas = preguntas_incorrectas
                resultado.preguntas_sin_responder = preguntas_sin_responder
                resultado.save()
            
            # Actualizar estadísticas de actividad del estudiante
            if examen.estudiante.is_student():
                try:
                    from accounts.models import UserActivityStats
                    activity_stats, created = UserActivityStats.objects.get_or_create(
                        user=examen.estudiante
                    )
                    activity_stats.update_exam_completed(examen.fecha_fin.date())
                    
                    # Obtener mensaje de milestone si lo hay
                    milestone_message = activity_stats.get_streak_milestone_message()
                    if milestone_message:
                        messages.success(request, milestone_message)
                except Exception as e:
                    # Log pero no fallar el examen
                    pass
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse_lazy('core:examen_resultado', kwargs={'examen_id': examen.id})
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class ExamenTestResultadoView(LoginRequiredMixin, DetailView):
    """Vista para mostrar resultados del examen"""
    model = ExamenTest
    template_name = 'core/examen/examen_resultado.html'
    context_object_name = 'examen'
    pk_url_kwarg = 'examen_id'

    def get_object(self):
        examen = super().get_object()
        if examen.estudiante != self.request.user and not self.request.user.is_admin():
            raise Http404("Examen no encontrado")
        return examen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Resultados: {self.object.nombre}'
        context['resultado'] = self.object.resultado
        context['respuestas'] = self.object.respuestas_examen.all().order_by('orden_pregunta')
        return context


class ExamenTestRankingView(LoginRequiredMixin, ListView):
    """Vista para mostrar ranking de estudiantes"""
    model = ExamenTestResultado
    template_name = 'core/examen/examen_ranking.html'
    context_object_name = 'resultados'
    paginate_by = 20

    def get_queryset(self):
        # Solo incluir exámenes realizados por estudiantes (excluir administradores)
        # Obtener todos los estudiantes con sus mejores resultados
        estudiantes = CustomUser.objects.filter(user_type='student')
        resultados_con_score = []
        
        for estudiante in estudiantes:
            # Obtener el mejor resultado tradicional (incluye resultados sin examen)
            mejor_resultado = ExamenTestResultado.objects.filter(
                estudiante=estudiante
            ).order_by('-porcentaje_acierto', 'tiempo_total_segundos').first()
            
            if mejor_resultado:
                # Calcular puntaje mejorado
                enhanced_score = estudiante.get_enhanced_ranking_score()
                mejor_resultado.enhanced_score = enhanced_score
                mejor_resultado.activity_stats = estudiante.get_activity_stats()
                resultados_con_score.append(mejor_resultado)
        
        # Ordenar por puntaje mejorado
        resultados_con_score.sort(key=lambda x: (-x.enhanced_score, x.tiempo_total_segundos))
        
        return resultados_con_score

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ranking de Estudiantes'
        
        # Obtener posición del usuario actual (solo si es estudiante)
        try:
            if self.request.user.is_student():
                user_resultados = ExamenTestResultado.objects.filter(
                    examen__estudiante=self.request.user,
                    examen__estudiante__user_type='student'
                ).order_by('-porcentaje_acierto', 'tiempo_total_segundos')
                
                if user_resultados.exists():
                    mejor_resultado = user_resultados.first()
                    todos_resultados = list(self.get_queryset())
                    posicion = todos_resultados.index(mejor_resultado) + 1
                    context['mi_posicion'] = posicion
                    context['mi_mejor_resultado'] = mejor_resultado
            else:
                # Si es administrador, no mostrar posición
                context['mi_posicion'] = None
                context['mi_mejor_resultado'] = None
        except:
            context['mi_posicion'] = None
            
        return context


class ExamenTestRetakeView(LoginRequiredMixin, TemplateView):
    """Vista para repetir un examen ya realizado con preguntas aleatorias"""
    
    def post(self, request, *args, **kwargs):
        """Crear un nuevo examen basado en uno ya completado"""
        try:
            examen_original_id = kwargs.get('examen_id')
            examen_original = get_object_or_404(ExamenTest, id=examen_original_id)
            
            # Verificar permisos
            if examen_original.estudiante != request.user and not request.user.is_admin():
                messages.error(request, 'No tienes permisos para repetir este examen.')
                return redirect('core:examen_test_list')
            
            # Verificar que el examen esté completado
            if not examen_original.completado:
                messages.error(request, 'Solo puedes repetir exámenes que ya hayas completado.')
                return redirect('core:examen_test_list')
            
            # Crear nuevo examen con la misma configuración
            nuevo_examen = ExamenTest.objects.create(
                estudiante=request.user,
                nombre=f"{examen_original.nombre} (Repetición)",
                tipo=examen_original.tipo,
                numero_preguntas=examen_original.numero_preguntas,
                tiempo_por_pregunta=examen_original.tiempo_por_pregunta,
                tipo_aclaracion=examen_original.tipo_aclaracion,
                fecha_inicio=timezone.now(),
                completado=False
            )
            
            # Copiar temas y apartados seleccionados
            nuevo_examen.temas_seleccionados.set(examen_original.temas_seleccionados.all())
            nuevo_examen.apartados_seleccionados.set(examen_original.apartados_seleccionados.all())
            
            # Actualizar estadísticas de repetición
            if request.user.is_student():
                try:
                    from accounts.models import UserActivityStats
                    activity_stats, created = UserActivityStats.objects.get_or_create(
                        user=request.user
                    )
                    activity_stats.update_exam_retaken()
                except Exception as e:
                    # Log pero no fallar la repetición
                    pass
            
            messages.success(request, 'Examen configurado para repetir con preguntas aleatorias.')
            return redirect('core:examen_ejecutar', examen_id=nuevo_examen.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el examen: {str(e)}')
            return redirect('core:examen_test_list')


class ExamenTestDeleteView(LoginRequiredMixin, TemplateView):
    """Vista para eliminar un examen manteniendo los resultados en el ranking"""
    
    def post(self, request, *args, **kwargs):
        """Eliminar examen pero conservar resultados para el ranking"""
        try:
            examen_id = kwargs.get('examen_id')
            examen = get_object_or_404(ExamenTest, id=examen_id)
            
            # Verificar permisos
            if examen.estudiante != request.user and not request.user.is_admin():
                messages.error(request, 'No tienes permisos para eliminar este examen.')
                return redirect('core:examen_test_list')
            
            # Verificar que el examen esté completado
            if not examen.completado:
                messages.error(request, 'Solo puedes eliminar exámenes completados.')
                return redirect('core:examen_test_list')
            
            # Verificar que tenga resultados
            if not hasattr(examen, 'resultado') or not examen.resultado:
                messages.error(request, 'Este examen no tiene resultados para conservar.')
                return redirect('core:examen_test_list')
            
            # Actualizar el resultado para que sea independiente del examen
            resultado = examen.resultado
            if not resultado.estudiante:  # Si no tiene estudiante asignado
                resultado.estudiante = examen.estudiante
            if not resultado.nombre_examen:  # Si no tiene nombre guardado
                resultado.nombre_examen = examen.nombre
            if not resultado.fecha_completado:  # Si no tiene fecha guardada
                resultado.fecha_completado = examen.fecha_fin
            if not resultado.tipo_examen:  # Si no tiene tipo guardado
                resultado.tipo_examen = examen.tipo
            
            # Guardar cambios en resultado antes de eliminar examen
            resultado.save()
            
            # Eliminar el examen (los resultados se conservan)
            nombre_examen = examen.nombre
            examen.delete()
            
            messages.success(
                request, 
                f'Examen "{nombre_examen}" eliminado exitosamente. '
                f'Los resultados se han conservado en el ranking.'
            )
            return redirect('core:examen_test_list')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar el examen: {str(e)}')
            return redirect('core:examen_test_list')