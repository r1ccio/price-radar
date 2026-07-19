from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Target, PriceHistory
from .serializers import TargetSerializer, PriceHistorySerializer
from .tasks import parse_target_price

# Create your views here.

class TargetViewSet(viewsets.ModelViewSet):

    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def perform_create(self, serializer):
        # on target creation set the user to the current authenticated user, else set it to the first user in db (testing purposes) 
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        target = serializer.save(user=user)
        parse_target_price.delay(target.id)


class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):

    # supports only GET-requsets (ReadOnly) as price history is immutable

    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer
