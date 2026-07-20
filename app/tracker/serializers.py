from rest_framework import serializers
from .models import Target, PriceHistory

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