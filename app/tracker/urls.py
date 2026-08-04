from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TargetViewSet, PriceHistoryViewSet, UserRegistrationView, UserProfileView, sync_telegram

router = DefaultRouter()
router.register(r'targets', TargetViewSet, basename='target')
router.register(r'price-history', PriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('sync-telegram/', sync_telegram, name='sync_telegram'),
    path('', include(router.urls)),
]