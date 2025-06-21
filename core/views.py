from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django import forms
from .models import Oposicion, Tema
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
            context['mis_oposiciones'] = user.oposiciones_acceso.all()[:5]
            context['mis_temas'] = user.temas_acceso.all()[:5]
            context['total_oposiciones'] = user.oposiciones_acceso.count()
            context['total_temas'] = user.temas_acceso.count()
        elif user.is_admin():
            context['total_oposiciones'] = Oposicion.objects.count()
            context['total_temas'] = Tema.objects.count()
            context['total_estudiantes'] = CustomUser.objects.filter(user_type='student').count()
            context['oposiciones_recientes'] = Oposicion.objects.order_by('-created_at')[:5]
            
        return context


# Vistas para Estudiantes
class OposicionListView(LoginRequiredMixin, ListView):
    """Lista de oposiciones para estudiantes"""
    model = Oposicion
    template_name = 'core/oposicion_list.html'
    context_object_name = 'oposiciones'
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_admin():
            return Oposicion.objects.all()
        return self.request.user.oposiciones_acceso.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Oposiciones'
        return context


class OposicionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de oposición"""
    model = Oposicion
    template_name = 'core/oposicion_detail.html'
    context_object_name = 'oposicion'

    def get_queryset(self):
        if self.request.user.is_admin():
            return Oposicion.objects.all()
        return self.request.user.oposiciones_acceso.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.nombre
        return context


class TemaListView(LoginRequiredMixin, ListView):
    """Lista de temas para estudiantes"""
    model = Tema
    template_name = 'core/tema_list.html'
    context_object_name = 'temas'
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_admin():
            return Tema.objects.all()
        return self.request.user.temas_acceso.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Temas'
        return context


class TemaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de tema"""
    model = Tema
    template_name = 'core/tema_detail.html'
    context_object_name = 'tema'

    def get_queryset(self):
        if self.request.user.is_admin():
            return Tema.objects.all()
        return self.request.user.temas_acceso.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.nombre
        return context


# Formularios para Admin
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
        # Hacer que el email sea requerido
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Configurar el campo is_active como checkbox
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
        self.fields['is_active'].label = 'Usuario Activo'
        
        # Si estamos editando un usuario existente, asegurar que is_active tenga el valor correcto
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
        # Establecer valores por defecto para nuevos usuarios
        self.fields['is_active'].initial = True
        self.fields['user_type'].initial = 'student'
        
        # Configurar el campo is_active como checkbox
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
        self.fields['is_active'].label = 'Usuario Activo'
        
        # Hacer campos requeridos
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
        fields = ['nombre', 'alumnos_con_acceso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'alumnos_con_acceso': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumnos_con_acceso'].queryset = CustomUser.objects.filter(user_type='student')


# Vistas para Administradores
class AdminOposicionListView(AdminRequiredMixin, ListView):
    """Lista de oposiciones para admin"""
    model = Oposicion
    template_name = 'core/admin/oposicion_list.html'
    context_object_name = 'oposiciones'
    paginate_by = 15

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


# Vistas similares para Temas
class AdminTemaListView(AdminRequiredMixin, ListView):
    model = Tema
    template_name = 'core/admin/tema_list.html'
    context_object_name = 'temas'
    paginate_by = 15

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
        # Prevenir que un admin se elimine a sí mismo
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