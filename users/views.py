from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, OTPVerifySerializer, ResendOTPSerializer



# Register View
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please check your email for the OTP."}, status=status.HTTP_201_CREATED)
        return Response({"registration failed, please try again"}, status=status.HTTP_400_BAD_REQUEST)


# OTP Verification View
class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Account verified successfully."}, status=status.HTTP_200_OK)
        return Response({"invalid OTP, please try again"}, status=status.HTTP_400_BAD_REQUEST)


# Resend OTP View
class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
