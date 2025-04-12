from django.contrib import admin
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign
# Register your models here.



@admin.register(AmazonAdsSaleAsin)
class AmazonAdsSaleAsinAdmin(admin.ModelAdmin):
    list_display = ('amazon_ads', 'asin', 'sales_date', 'sales', 'units_sold', 'cost', 'impressions', 'clicks', 'spend', 'cpc', 'orders', "campaign_type")
    list_filter = ('amazon_ads', 'sales_date', "campaign_type")
    search_fields = ('asin',)
    ordering = ('-sales_date',)
    readonly_fields = ("amazon_ads",)


@admin.register(AmazonAdsSaleCampaign)
class AmazonAdsSaleCampaignAdmin(admin.ModelAdmin):
    list_display = ('amazon_ads', 'campaign_name', 'sales_date', 'sales', 'units_sold', 'cost', 'impressions', 'clicks', 'spend', 'cpc', 'orders', "campaign_type")
    list_filter = ('amazon_ads', 'sales_date', "campaign_type")
    search_fields = ('campaign_name', 'campaign_id')
    ordering = ('-sales_date',)
    readonly_fields = ("amazon_ads",)
