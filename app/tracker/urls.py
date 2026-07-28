from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TargetViewSet, PriceHistoryViewSet, sync_telegram

router = DefaultRouter()
router.register(r'targets', TargetViewSet, basename='target')
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('sync-telegram/', sync_telegram, name='sync_telegram'),
    path('', include(router.urls)),
]