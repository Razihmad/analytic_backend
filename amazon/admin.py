from django.contrib import admin

# Register your models here.
from amazon.models import Seller, SellerCentralSale, RegionDetail, SellerCentralTraffic

admin.site.register(Seller)
# admin.site.register(SellerCentralSale)
admin.site.register(RegionDetail)
# admin.site.register(SellerCentralTraffic)


@admin.register(SellerCentralSale)
class SellerCentralSaleAdmin(admin.ModelAdmin):
    list_display = ('seller', 'child_asin', 'parent_asin', 'sales_date', 'units_ordered', 'ordered_product_sales', 'items_ordered')
    list_filter = ('seller', 'sales_date')
    search_fields = ('child_asin', 'parent_asin')
    ordering = ('-sales_date',)


@admin.register(SellerCentralTraffic)
class SellerCentralTrafficAdmin(admin.ModelAdmin):
    list_display = ('seller', 'child_asin', 'sessions_date', 'sku', 'browser_sessions', 'mobile_app_sessions', 'browser_page_views', 'mobile_app_page_views', 'unit_sessions_percentage')
    list_filter = ('seller', 'sessions_date')
    search_fields = ('child_asin', 'sku')
    ordering = ('-sessions_date',)
