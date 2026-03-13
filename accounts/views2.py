import random
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .models import RegistrationOTP, Profile
from .serializers import *


# Create your views here.
class RegisterAPIView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            data = serializer.validated_data

            if data["password"] != data["confirm_password"]:
                return Response({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(username=data["username"]).exists():
                return Response({"error": "Username already exists"}, status=400)

            if User.objects.filter(email=data["email"]).exists():
                return Response({"error": "Email already registered"}, status=400)

            otp = str(random.randint(100000, 999999))

            otp_obj = RegistrationOTP.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                username=data["username"],
                email=data["email"],
                password=data["password"],
                otp=otp
            )

            send_mail(
                "Verify your account",
                f"Your OTP is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [data["email"]],
            )

            return Response({
                "message": "OTP sent to email",
                "otp_id": otp_obj.id
            })

        return Response(serializer.errors, status=400)

class VerifyOTPAPIView(APIView):

    def post(self, request, otp_id):

        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid():

            try:
                reg_data = RegistrationOTP.objects.get(id=otp_id)
            except RegistrationOTP.DoesNotExist:
                return Response({"error": "Invalid verification request"}, status=400)

            if timezone.now() - reg_data.created_at > timezone.timedelta(minutes=10):
                reg_data.delete()
                return Response({"error": "OTP expired"}, status=400)

            if reg_data.otp != serializer.validated_data["otp"]:
                return Response({"error": "Invalid OTP"}, status=400)

            user = User.objects.create_user(
                username=reg_data.username,
                email=reg_data.email,
                password=reg_data.password,
                first_name=reg_data.first_name,
                last_name=reg_data.last_name
            )

            Profile.objects.create(user=user)

            reg_data.delete()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Account created successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response(serializer.errors, status=400)

class LoginAPIView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            login_input = serializer.validated_data["login_input"]
            password = serializer.validated_data["password"]

            if "@" in login_input:
                try:
                    user_obj = User.objects.get(email=login_input)
                    username = user_obj.username
                except User.DoesNotExist:
                    return Response({"error": "Invalid credentials"}, status=400)
            else:
                username = login_input

            user = authenticate(username=username, password=password)

            if user is None:
                return Response({"error": "Invalid credentials"}, status=400)

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response(serializer.errors, status=400)

class ForgotPasswordAPIView(APIView):

    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data["email"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "No account with this email"}, status=400)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse("reset_password", kwargs={"uidb64": uid, "token": token})
            )

            send_mail(
                "Reset Password",
                f"Reset your password using link:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )

            return Response({"message": "Password reset link sent"})

        return Response(serializer.errors, status=400)

class ResetPasswordAPIView(APIView):

    def post(self, request, uidb64, token):

        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except:
                return Response({"error": "Invalid link"}, status=400)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=400)

            password = serializer.validated_data["password"]
            confirm_password = serializer.validated_data["confirm_password"]

            if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=400)

            user.set_password(password)
            user.save()

            return Response({"message": "Password reset successful"})

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"message": "Logout successful"})