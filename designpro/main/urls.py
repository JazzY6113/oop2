from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('applications/', views.applications_view, name='applications'),
    path('application/create/', views.application_create_view, name='application_create'),
    path('application/delete/<int:id>/', views.application_delete_view, name='application_delete'),
    path('application/change_status/<int:id>/', views.change_application_status, name='change_application_status'),
    path('manage_categories/', views.manage_categories, name='manage_categories'),
]