from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Target (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='targets', verbose_name='User')
    url = models.URLField(max_length=500, verbose_name='Item URL')
    title = models.CharField(max_length=200, blank=True, verbose_name='Item Title')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Current Price')
    target_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Target Price')
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram Chat ID for notifications")
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last Updation Date')


    class Meta:
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Target #{self.id} -{self.url[:30]}..."
    
class PriceHistory(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='price_history', verbose_name='Target')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fixed Price')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Check date')

    class Meta:
        verbose_name = 'Price History Log'
        verbose_name_plural = 'Price History Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.target} - {self.price} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
