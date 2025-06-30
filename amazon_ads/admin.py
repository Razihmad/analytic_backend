from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm
# Register your models here.


@admin.register(AmazonAdsSaleAsin)
class AmazonAdsSaleAsinAdmin(admin.ModelAdmin):
    list_display = ('amazon_ads', 'asin', 'sales_date', 'sales', 'units_sold', 'cost', 'impressions', 'clicks', 'spend', 'cpc', 'orders', "campaign_type")
    list_filter = ('amazon_ads', ('sales_date', DateRangeFilter), "campaign_type")
    search_fields = ('asin',)
    ordering = ('-sales_date',)
    readonly_fields = ("amazon_ads",)


@admin.register(AmazonAdsSaleCampaign)
class AmazonAdsSaleCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'amazon_ads', 'campaign_name', "campaign_bidding_strategy", 'sales_date', 'sales', 'impressions', 'clicks', 'spend', 'cpc', 'orders', "campaign_type"
    )
    list_filter = ('amazon_ads', ('sales_date', DateRangeFilter), "campaign_type")
    search_fields = ('campaign_name',)
    ordering = ('-sales_date',)
    readonly_fields = ("amazon_ads",)


@admin.register(SearchTerm)
class SearchTerm(admin.ModelAdmin):
    list_display = ("seller", "search_term", "search_term_date", "keyword", "targeting", "campaign_name","ad_group_name", "impressions", "clicks", "orders", "sales")
    search_fields = ("search_term", "keyword", "targeting", "campaign_name")
    # ordering = ("-search_term_date",)
    readonly_fields = ("seller",)

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.filter(seller=request.user)