from rest_framework import serializers
from .models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

# 1. Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'user_name', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            user_name=validated_data['user_name'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        user.is_active = False  # Prevent login until verified
        user.generate_otp()  # Generate and save OTP

        # Send OTP to user's email
        send_mail(
            subject='Verify Your Email - OTP Code',
            message=f'Your code is: {user.otp} use it to access your account. if you did not request this, please ignore.'
            'yours, The instagram clone Team',
            from_email='no-reply@myproject.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user

# 2. OTP Verification Serializer
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email, otp=otp)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP.")

        # Optional: Check if OTP is expired
        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=1):
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        # Mark user as verified
        user.is_verified = True
        user.is_active = True
        user.otp = None
        user.otp_created_at = None
        user.save()

        return data

# 3. Resend OTP Serializer
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.is_verified:
            raise serializers.ValidationError("Account already verified.")

        return email

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        user.generate_otp()  # regenerate OTP

        # Send new OTP to email
        send_mail(
            subject='Your New OTP Code',
            message=f'Your new code is: {user.otp} Use it to verify your account.'
            'if you did not request for this, please ignore',
            from_email='no-reply@myproject.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Accepts either username or email
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        # Try email first
        user = User.objects.filter(email__iexact=identifier).first()

        # If not found by email, try username
        if not user:
            user = User.objects.filter(user_name__iexact=identifier).first()

        if not user:
            raise AuthenticationFailed("User not found.")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password.")

        if not user.is_verified:
            raise AuthenticationFailed("Account is not verified.")

        data['user'] = user
        return data

#request for a password    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return email

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        user.generate_otp()  # Use existing OTP generation on User model

        send_mail(
            subject='Password Reset OTP',
            message=f'Your OTP for password reset is: {user.otp}',
            from_email='no-reply@myproject.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
#verify OTP    
class PasswordResetOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']

        try:
            user = User.objects.get(email=email, otp=otp)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=10):
            raise serializers.ValidationError("OTP has expired.")

        # If valid, we can set a flag or just proceed
        # We'll just return user for now
        data['user'] = user
        return data

#set new password
class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        email = data['email']
        otp = data['otp']

        try:
            user = User.objects.get(email=email, otp=otp)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=10):
            raise serializers.ValidationError("OTP has expired.")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.otp = None
        user.otp_created_at = None
        user.save()