from django.urls import path
from .views import *
from . import views
urlpatterns = [
    path('register/', register, name='accountRegister'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name = 'accountLogin'),
    path('logout/', logout_view, name='accountLogout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]