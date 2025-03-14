from django.contrib import admin

# Register your models here.
from amazon.models import Seller, SellerCentralSale, RegionDetail

admin.site.register(Seller)
admin.site.register(SellerCentralSale)
admin.site.register(RegionDetail)
