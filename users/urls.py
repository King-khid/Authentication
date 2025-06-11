from django.urls import path
from .views import RegisterView, OTPVerifyView, ResendOTPView
from .views import LoginView
from .views import (
    LoginView,
    PasswordResetRequestView,
    PasswordResetOTPVerifyView,
    SetNewPasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    #password reset
    path("request-password/", PasswordResetRequestView.as_view()),
    path("verify-password/", PasswordResetOTPVerifyView.as_view()),
    path("reset-password/", SetNewPasswordView.as_view()),
]