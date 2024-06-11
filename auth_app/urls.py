from . import views
from django.urls import path

app_name = 'auth_app'
urlpatterns = [
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/',views.register,name='register'),
    path('loginOrRegister/',views.loginOrRegister,name='loginOrRegister'),
]