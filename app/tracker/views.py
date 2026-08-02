from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
import uuid
from .models import Target, PriceHistory, UserProfile
from .serializers import TargetSerializer, PriceHistorySerializer
from .tasks import parse_target_price

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def sync_telegram(request):
    token = request.data.get('token')
    chat_id = request.data.get('chat_id')

    if not token or not chat_id:
        return Response({"error": "Missing token or chat_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = UserProfile.objects.get(sync_token=token)
        profile.telegram_chat_id = str(chat_id)
        profile.sync_token = uuid.uuid4()
        profile.save()
        return Response({"message": "Account linked successfully"}, status=status.HTTP_200_OK)
    except (UserProfile.DoesNotExist, ValueError):
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_404_NOT_FOUND)


class TargetViewSet(viewsets.ModelViewSet):

    serializer_class = TargetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Target.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        chat_id = self.request.data.get('telegram_chat_id')
        assigned_user = self.request.user # default to the current authenticated user

        if chat_id:
            profile = UserProfile.objects.filter(telegram_chat_id=chat_id).first()
            if profile:
                assigned_user = profile.user

        # serializer.save(user=assigned_user)
        # on target creation set the user to the current authenticated user, else set it to the first user in db (testing purposes) 
        # user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        target = serializer.save(user=assigned_user)
        parse_target_price.delay(target.id)


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):

    # supports only GET-requsets (ReadOnly) as price history is immutable

    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PriceHistory.objects.filter(target__user=self.request.user)
