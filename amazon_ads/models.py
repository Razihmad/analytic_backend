from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AmazonAdsAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=500)
    marketplace_id = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=255)
    amazon_seller_id = models.CharField(max_length=255)
    profile_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'amazon_seller_id', "marketplace_id"]
