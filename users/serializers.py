from rest_framework import serializers
from .models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

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
            message=f'Your OTP is: {user.otp}',
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
        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=10):
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
            message=f'Your new OTP is: {user.otp}',
            from_email='no-reply@myproject.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
