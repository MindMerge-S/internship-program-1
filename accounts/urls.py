from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='accountRegister'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name = 'accountLogin'),
    path('logout/', logout_view, name='accountLogout'),
]