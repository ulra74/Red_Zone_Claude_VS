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
from .models import Oposicion, Tema, TemaOposicion
from accounts.models import CustomUser


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de administrador"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return super().handle_no_permission()


class HomeView(TemplateView):
    """Vista de la página principal"""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Red Zone Academy'
        context['oposiciones_count'] = Oposicion.objects.count()
        context['temas_count'] = Tema.objects.count()
        return context


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
            
        elif user.is_admin():
            context['total_oposiciones'] = Oposicion.objects.count()
            context['total_temas'] = Tema.objects.count()
            context['total_estudiantes'] = CustomUser.objects.filter(user_type='student').count()
            context['oposiciones_recientes'] = Oposicion.objects.prefetch_related('temas').order_by('-created_at')[:5]
            
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
        context['temas'] = temas_oposicion
        
        # Estadísticas para estudiantes
        if self.request.user.is_student():
            context['progreso_temas'] = {}
            for tema in temas_oposicion:
                # Aquí puedes calcular el progreso del estudiante en cada tema
                context['progreso_temas'][tema.id] = {
                    'completado': False,  # Implementar lógica de progreso
                    'porcentaje': 0,
                }
        
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
        
        # Obtener oposiciones relacionadas
        context['oposiciones_relacionadas'] = self.object.oposiciones.all()
        
        return context


# Formularios actualizados
class OposicionForm(forms.ModelForm):
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


class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nombre', 'descripcion', 'oposiciones', 'alumnos_con_acceso', 'orden', 'es_obligatorio', 'peso_evaluacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'oposiciones': forms.CheckboxSelectMultiple(),
            'alumnos_con_acceso': forms.CheckboxSelectMultiple(),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_evaluacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumnos_con_acceso'].queryset = CustomUser.objects.filter(user_type='student')
        self.fields['oposiciones'].queryset = Oposicion.objects.all()
        
        # Configurar checkbox para es_obligatorio
        self.fields['es_obligatorio'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })


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
    form_class = OposicionForm
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
    form_class = OposicionForm
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