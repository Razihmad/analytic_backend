from django.contrib import admin
from amazon_ads.models import AmazonAdsAccount, AmazonAdsSaleAsin, AmazonAdsSaleCampaign
# Register your models here.


admin.site.register(AmazonAdsAccount)
admin.site.register(AmazonAdsSaleAsin)
admin.site.register(AmazonAdsSaleCampaign)
