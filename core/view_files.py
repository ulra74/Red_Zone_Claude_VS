from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.utils.encoding import smart_str
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django import forms
import os
import mimetypes

from .models import (
    ArchivoOposicion, ArchivoTema, Oposicion, Tema, 
    DescargaArchivo, TipoArchivo
)
from accounts.models import CustomUser


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ArchivoOposicionForm(forms.ModelForm):
    class Meta:
        model = ArchivoOposicion
        fields = ['nombre', 'descripcion', 'archivo', 'tipo', 'es_publico']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'es_publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].help_text = "Nombre descriptivo para el archivo"
        self.fields['descripcion'].help_text = "Descripción opcional del contenido"
        self.fields['archivo'].help_text = "Archivos permitidos: PDF, DOC, PPT, MP4, MP3, imágenes (máx. 50MB)"
        self.fields['es_publico'].help_text = "Visible para todos los estudiantes con acceso"


class ArchivoTemaForm(forms.ModelForm):
    class Meta:
        model = ArchivoTema
        fields = ['nombre', 'descripcion', 'archivo', 'tipo', 'orden', 'es_publico']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'es_publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].help_text = "Nombre descriptivo para el archivo"
        self.fields['descripcion'].help_text = "Descripción opcional del contenido"
        self.fields['archivo'].help_text = "Archivos permitidos: PDF, DOC, PPT, MP4, MP3, imágenes (máx. 50MB)"
        self.fields['orden'].help_text = "Orden de aparición (0 = primero)"
        self.fields['es_publico'].help_text = "Visible para todos los estudiantes con acceso"


class SubirArchivoOposicionView(LoginRequiredMixin, CreateView):
    """Vista para subir archivos a una oposición"""
    model = ArchivoOposicion
    form_class = ArchivoOposicionForm
    template_name = 'core/files/subir_archivo_oposicion.html'

    def dispatch(self, request, *args, **kwargs):
        self.oposicion = get_object_or_404(Oposicion, pk=kwargs['oposicion_id'])
        # Solo admins pueden subir archivos
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para subir archivos.')
            return redirect('core:oposicion_detail', pk=self.oposicion.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.oposicion = self.oposicion
        form.instance.subido_por = self.request.user
        messages.success(self.request, f'Archivo "{form.instance.nombre}" subido exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:oposicion_detail', kwargs={'pk': self.oposicion.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oposicion'] = self.oposicion
        context['title'] = f'Subir Archivo - {self.oposicion.nombre}'
        return context


class SubirArchivoTemaView(LoginRequiredMixin, CreateView):
    """Vista para subir archivos a un tema"""
    model = ArchivoTema
    form_class = ArchivoTemaForm
    template_name = 'core/files/subir_archivo_tema.html'

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=kwargs['tema_id'])
        # Solo admins pueden subir archivos
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para subir archivos.')
            return redirect('core:tema_detail', pk=self.tema.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tema = self.tema
        form.instance.subido_por = self.request.user
        messages.success(self.request, f'Archivo "{form.instance.nombre}" subido exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:tema_detail', kwargs={'pk': self.tema.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        context['title'] = f'Subir Archivo - {self.tema.nombre}'
        return context


class ArchivosOposicionListView(LoginRequiredMixin, ListView):
    """Lista de archivos de una oposición"""
    model = ArchivoOposicion
    template_name = 'core/files/archivos_oposicion_list.html'
    context_object_name = 'archivos'
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        self.oposicion = get_object_or_404(Oposicion, pk=kwargs['oposicion_id'])
        
        # Verificar acceso
        if request.user.is_student():
            if self.oposicion not in request.user.oposiciones_acceso.all():
                messages.error(request, 'No tienes acceso a esta oposición.')
                return redirect('core:oposicion_list')
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_admin():
            return self.oposicion.archivos.all()
        else:
            # Solo archivos públicos para estudiantes
            return self.oposicion.archivos.filter(es_publico=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oposicion'] = self.oposicion
        context['title'] = f'Archivos - {self.oposicion.nombre}'
        context['puede_subir'] = self.request.user.is_admin()
        return context


class ArchivosTemaListView(LoginRequiredMixin, ListView):
    """Lista de archivos de un tema"""
    model = ArchivoTema
    template_name = 'core/files/archivos_tema_list.html'
    context_object_name = 'archivos'
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=kwargs['tema_id'])
        
        # Verificar acceso
        if request.user.is_student():
            if self.tema not in request.user.temas_acceso.all():
                messages.error(request, 'No tienes acceso a este tema.')
                return redirect('core:tema_list')
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_admin():
            return self.tema.archivos.all()
        else:
            # Solo archivos públicos para estudiantes
            return self.tema.archivos.filter(es_publico=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tema'] = self.tema
        context['title'] = f'Archivos - {self.tema.nombre}'
        context['puede_subir'] = self.request.user.is_admin()
        return context


@login_required
def descargar_archivo_oposicion(request, archivo_id):
    """Descarga un archivo de oposición"""
    archivo = get_object_or_404(ArchivoOposicion, pk=archivo_id)
    
    # Verificar permisos
    if request.user.is_student():
        # Verificar acceso a la oposición
        if archivo.oposicion not in request.user.oposiciones_acceso.all():
            raise Http404("No tienes acceso a este archivo")
        
        # Verificar si el archivo es público
        if not archivo.es_publico:
            raise Http404("Este archivo no está disponible")
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo.archivo.path):
        messages.error(request, 'El archivo ya no está disponible.')
        return redirect('core:oposicion_detail', pk=archivo.oposicion.pk)
    
    # Registrar la descarga
    DescargaArchivo.objects.create(
        usuario=request.user,
        archivo_oposicion=archivo,
        ip_address=get_client_ip(request)
    )
    
    # Incrementar contador de descargas
    archivo.descargas += 1
    archivo.save(update_fields=['descargas'])
    
    # Servir el archivo
    try:
        response = FileResponse(
            archivo.archivo.open('rb'),
            as_attachment=True,
            filename=smart_str(f"{archivo.nombre}{archivo.extension}")
        )
        
        # Determinar el tipo MIME
        content_type, _ = mimetypes.guess_type(archivo.archivo.path)
        if content_type:
            response['Content-Type'] = content_type
            
        return response
    except Exception as e:
        messages.error(request, 'Error al descargar el archivo.')
        return redirect('core:oposicion_detail', pk=archivo.oposicion.pk)


@login_required
def descargar_archivo_tema(request, archivo_id):
    """Descarga un archivo de tema"""
    archivo = get_object_or_404(ArchivoTema, pk=archivo_id)
    
    # Verificar permisos
    if request.user.is_student():
        # Verificar acceso al tema
        if archivo.tema not in request.user.temas_acceso.all():
            raise Http404("No tienes acceso a este archivo")
        
        # Verificar si el archivo es público
        if not archivo.es_publico:
            raise Http404("Este archivo no está disponible")
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo.archivo.path):
        messages.error(request, 'El archivo ya no está disponible.')
        return redirect('core:tema_detail', pk=archivo.tema.pk)
    
    # Registrar la descarga
    DescargaArchivo.objects.create(
        usuario=request.user,
        archivo_tema=archivo,
        ip_address=get_client_ip(request)
    )
    
    # Incrementar contador de descargas
    archivo.descargas += 1
    archivo.save(update_fields=['descargas'])
    
    # Servir el archivo
    try:
        response = FileResponse(
            archivo.archivo.open('rb'),
            as_attachment=True,
            filename=smart_str(f"{archivo.nombre}{archivo.extension}")
        )
        
        # Determinar el tipo MIME
        content_type, _ = mimetypes.guess_type(archivo.archivo.path)
        if content_type:
            response['Content-Type'] = content_type
            
        return response
    except Exception as e:
        messages.error(request, 'Error al descargar el archivo.')
        return redirect('core:tema_detail', pk=archivo.tema.pk)


class EliminarArchivoOposicionView(LoginRequiredMixin, DeleteView):
    """Eliminar archivo de oposición"""
    model = ArchivoOposicion
    template_name = 'core/files/eliminar_archivo_oposicion.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo admins pueden eliminar archivos
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para eliminar archivos.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Archivo eliminado exitosamente.')
        return reverse_lazy('core:oposicion_detail', kwargs={'pk': self.object.oposicion.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar {self.object.nombre}'
        return context


class EliminarArchivoTemaView(LoginRequiredMixin, DeleteView):
    """Eliminar archivo de tema"""
    model = ArchivoTema
    template_name = 'core/files/eliminar_archivo_tema.html'

    def dispatch(self, request, *args, **kwargs):
        # Solo admins pueden eliminar archivos
        if not request.user.is_admin():
            messages.error(request, 'No tienes permisos para eliminar archivos.')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Archivo eliminado exitosamente.')
        return reverse_lazy('core:tema_detail', kwargs={'pk': self.object.tema.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar {self.object.nombre}'
        return context