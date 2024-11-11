from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('send/', views.send_bulk_email, name='send_bulk_email'),
    path('logs/', views.email_logs, name='email_logs'),
]