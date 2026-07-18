from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TargetViewSet, PriceHistoryViewSet

router = DefaultRouter()
router.register(r'targets', TargetViewSet, basename='target')
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('', include(router.urls)),
]