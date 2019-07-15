from django.urls import path, include
from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]

