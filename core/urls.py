from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Oposiciones
    path('oposiciones/', views.OposicionListView.as_view(), name='oposicion_list'),
    path('oposiciones/<int:pk>/', views.OposicionDetailView.as_view(), name='oposicion_detail'),
    
    # Temas
    path('temas/', views.TemaListView.as_view(), name='tema_list'),
    path('temas/<int:pk>/', views.TemaDetailView.as_view(), name='tema_detail'),
    
    # Admin URLs (solo para administradores)
    path('admin/oposiciones/', views.AdminOposicionListView.as_view(), name='admin_oposicion_list'),
    path('admin/oposiciones/create/', views.AdminOposicionCreateView.as_view(), name='admin_oposicion_create'),
    path('admin/oposiciones/<int:pk>/edit/', views.AdminOposicionUpdateView.as_view(), name='admin_oposicion_update'),
    path('admin/oposiciones/<int:pk>/delete/', views.AdminOposicionDeleteView.as_view(), name='admin_oposicion_delete'),
    
    path('admin/temas/', views.AdminTemaListView.as_view(), name='admin_tema_list'),
    path('admin/temas/create/', views.AdminTemaCreateView.as_view(), name='admin_tema_create'),
    path('admin/temas/<int:pk>/edit/', views.AdminTemaUpdateView.as_view(), name='admin_tema_update'),
    path('admin/temas/<int:pk>/delete/', views.AdminTemaDeleteView.as_view(), name='admin_tema_delete'),
    
    # Gestión de usuarios (solo admin)
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/create/', views.AdminUserCreateView.as_view(), name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.AdminUserUpdateView.as_view(), name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
]