from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import CustomUser, VendorProfile, TravelerProfile, OTP
import random
from django.core.mail import send_mail
from django.conf import settings

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'id': self.user.id,
            'name': self.user.name,
            'email': self.user.email,
            'role': self.user.role,
        }
        return data

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'username', 'password', 'confirm_password', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', 'traveler'),
            is_verified=False
        )
        if user.role == 'vendor':
            VendorProfile.objects.create(user=user)
        elif user.role == 'traveler':
            TravelerProfile.objects.create(user=user)
        # Generate and send OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        OTP.objects.create(user=user, code=otp_code)
        send_mail(
            'Verify Your TrekBot Account',
            f'Your OTP is {otp_code}. It is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
            otp_obj = OTP.objects.filter(user=user, is_used=False).latest('created_at')
            if otp_obj.is_expired() or otp_obj.code != data['otp']:
                raise serializers.ValidationError("Invalid or expired OTP.")
            return data
        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError("Invalid email or OTP.")

class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['id', 'business_name']

class TravelerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelerProfile
        fields = ['id', 'travel_history']