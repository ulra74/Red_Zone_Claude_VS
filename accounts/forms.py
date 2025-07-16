from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico',
            'id': 'email'
        }),
        label='Correo electrónico'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'id': 'password'
        }),
        label='Contraseña'
    )

class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'profile_picture': 'Foto de Perfil'
        }
        help_texts = {
            'profile_picture': 'Formatos permitidos: JPG, PNG, GIF. Tamaño máximo: 2MB'
        }
    
    def clean_profile_picture(self):
        """Validar el tamaño y formato de la imagen"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Verificar el tamaño (2MB máximo)
            if profile_picture.size > 2 * 1024 * 1024:
                raise forms.ValidationError("La imagen debe ser menor a 2MB")
            
            # Verificar el formato
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif']
            if profile_picture.content_type not in allowed_formats:
                raise forms.ValidationError("Solo se permiten archivos JPG, PNG o GIF")
        
        return profile_picture