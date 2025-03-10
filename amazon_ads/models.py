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


class AmazonAdsSaleAsin(models.Model):
    amazon_ads = models.ForeignKey(AmazonAdsAccount, on_delete=models.CASCADE)
    asin = models.CharField(max_length=255)
    sales_date = models.DateField()
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    cpc = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['amazon_ads', 'asin', 'sales_date']


class AmazonAdsSaleCampaign(models.Model):
    amazon_ads = models.ForeignKey(AmazonAdsAccount, on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255)
    sales_date = models.DateField()
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    cpc = models.DecimalField(max_digits=10, decimal_places=2)
    campaign_bidding_strategy = models.CharField(max_length=255, null=True, blank=True)
    campaign_status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['amazon_ads', 'campaign_id', 'sales_date']
