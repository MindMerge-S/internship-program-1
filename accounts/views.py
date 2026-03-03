from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import random
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

# Create your views here.
@login_required(login_url='accountLogin')
def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('accountRegister')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('accountRegister')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('accountRegister')

        otp = str(random.randint(100000, 999999))

        request.session['registration_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'password': password,
            'otp': otp,
            'otp_created_at': timezone.now().timestamp()
        }

        # 6️⃣ Send OTP Email
        send_mail(
            'Verify your account',
            f'Your OTP is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect('verify_otp')

    return render(request, 'accounts/register.html')

def verify_otp(request):
    reg_data = request.session.get('registration_data')

    if not reg_data:
        messages.error(request, "Session expired. Please register again.")
        return redirect('accountRegister')

    if request.method == 'POST':
        user_otp = request.POST.get('otp')

        # OTP Expiry check (10 min)
        otp_time = float(reg_data['otp_created_at'])
        if timezone.now().timestamp() - otp_time > 600:
            del request.session['registration_data']
            messages.error(request, "OTP expired.")
            return redirect('accountRegister')

        # OTP Match
        if reg_data['otp'] == user_otp:

            # Create User NOW
            new_user = User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password'],
                first_name=reg_data['first_name'],
                last_name=reg_data['last_name']
            )

            # Create Profile
            Profile.objects.create(user=new_user)

            # Clear session
            del request.session['registration_data']

            login(request, new_user)
            messages.success(request, "Account created successfully!")
            return redirect('home')

        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'accounts/verify_otp.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        login_input = request.POST.get('login_input')  # username OR email
        password = request.POST.get('password')

        # Check if input is email
        user_obj = None
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, "Invalid credentials.")
                return redirect('accountLogin')
        else:
            username = login_input
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'accounts/login.html')

@login_required(login_url='accountLogin')
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')