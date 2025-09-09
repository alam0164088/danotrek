from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, VerifyOTPSerializer, VendorProfileSerializer, TravelerProfileSerializer
from .models import CustomUser, VendorProfile, TravelerProfile, OTP

class AuthViewSet(viewsets.ViewSet):
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role},
                'message': 'Please verify your email with the OTP sent to you.'
            }
            if user.role == 'vendor':
                response_data['profile'] = VendorProfileSerializer(VendorProfile.objects.get(user=user)).data
            elif user.role == 'traveler':
                response_data['profile'] = TravelerProfileSerializer(TravelerProfile.objects.get(user=user)).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = serializer.user
            if not user.is_verified:
                return Response({'error': 'Please verify your email first.'}, status=status.HTTP_403_FORBIDDEN)
            response_data = data
            if user.role == 'vendor':
                response_data['profile'] = VendorProfileSerializer(VendorProfile.objects.get(user=user)).data
            elif user.role == 'traveler':
                response_data['profile'] = TravelerProfileSerializer(TravelerProfile.objects.get(user=user)).data
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def verify_otp(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            otp_obj = OTP.objects.filter(user=user, is_used=False).latest('created_at')
            otp_obj.is_used = True
            otp_obj.save()
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)