from django.contrib import admin

# Register your models here.
from amazon.models import Seller, SellerCentralSale, RegionDetail, SellerCentralTraffic

admin.site.register(Seller)
admin.site.register(SellerCentralSale)
admin.site.register(RegionDetail)
admin.site.register(SellerCentralTraffic)
