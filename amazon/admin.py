from django.contrib import admin

# Register your models here.
from amazon.models import Seller, SellerCentralSale

admin.site.register(Seller)
admin.site.register(SellerCentralSale)
