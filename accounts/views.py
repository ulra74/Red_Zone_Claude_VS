from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from .models import CustomUser


class CustomLoginView(LoginView):
    """Vista de login personalizada"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido/a, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Si no tienes cuenta, contacta con el administrador.')
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    """Vista del perfil del usuario"""
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi Perfil'
        context['oposiciones_count'] = self.object.oposiciones_acceso.count()
        context['temas_count'] = self.object.temas_acceso.count()
        return context


class ProfileEditForm(forms.ModelForm):
    """Formulario para editar perfil"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vista para editar perfil"""
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Perfil'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)