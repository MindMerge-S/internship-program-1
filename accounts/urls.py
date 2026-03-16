from django.urls import path
from .views import *
from . import views
# urlpatterns = [
#     path('register/', RegisterAPIView.as_view(), name='accountRegister'),
#     path('verify-otp/<int:otp_id>/', VerifyOTPAPIView.as_view(), name='verify_otp'),
#     path('login/', LoginAPIView.as_view(), name = 'accountLogin'),

#     path('logout/', LogoutAPIView.as_view(), name='accountLogout'),
    
#     path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
#     path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset_password'),
# ]
urlpatterns = [
    path('register/', register, name='accountRegister'),
    path('verify-otp/<int:otp_id>/', verify_otp, name='verify_otp'),
    path('login/', login_view, name = 'accountLogin'),

    path('logout/', logout_view, name='accountLogout'),
    
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    
    path('profile/', profile, name = 'accountProfile'),
]