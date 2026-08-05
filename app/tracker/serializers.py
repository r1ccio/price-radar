from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Target, PriceHistory, UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['telegram_chat_id', 'sync_token', 'fcm_token']
        read_only_fields = ['sync_token']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'price', 'created_at']
        read_only_fields = ['id', 'price', 'created_at']
    

class TargetSerializer(serializers.ModelSerializer):
    price_history = PriceHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Target
        fields = ['id', 'url', 'title', 'current_price', 'target_price', 'telegram_chat_id', 'is_active', 'created_at', 'updated_at', 'price_history']
        read_only_fields = ['id', 'title', 'current_price', 'created_at', 'updated_at', 'price_history']