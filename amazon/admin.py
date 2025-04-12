from django.contrib import admin
from rangefilter.filters import DateRangeFilter

# Register your models here.
from amazon.models import Seller, SellerCentralSale, RegionDetail, SellerCentralTraffic


@admin.register(SellerCentralSale)
class SellerCentralSaleAdmin(admin.ModelAdmin):
    list_display = ('seller', 'child_asin', 'parent_asin', 'sales_date', 'units_ordered', 'sales', 'orders')
    list_filter = ('seller', ('sales_date', DateRangeFilter))
    search_fields = ('child_asin', 'parent_asin')
    ordering = ('-sales_date',)
    readonly_fields = ("seller",)


@admin.register(SellerCentralTraffic)
class SellerCentralTrafficAdmin(admin.ModelAdmin):
    list_display = (
        'seller', 'child_asin', 'sessions_date', 'sku', 'browser_sessions', 'mobile_app_sessions', 'browser_page_views', 'mobile_app_page_views', 'unit_sessions_percentage', "total_sessions", "total_page_views"
    )
    list_filter = ('seller', ('sessions_date', DateRangeFilter))
    search_fields = ('child_asin', 'sku')
    ordering = ('-sessions_date',)
    readonly_fields = ("seller", )


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'marketplace_id', 'marketplace', 'store_name', 'refresh_token', 'ads_refresh_token', 'profile_id', 'amazon_seller_id', 'country_code', 'created_at', 'updated_at')
    list_filter = ('user', 'marketplace')
    search_fields = ('amazon_seller_id', 'store_name')
    ordering = ('-created_at',)
    readonly_fields = ("user",)


@admin.register(RegionDetail)
class RegionDetailAdmin(admin.ModelAdmin):
    list_display = ('marketplace_id', 'country', 'country_code', 'region', 'is_active')
    list_filter = ('marketplace_id', 'is_active')
    search_fields = ('country', 'region')
    ordering = ('marketplace_id',)
