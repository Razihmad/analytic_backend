from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class MarketPlace(models.Model):
    name = models.CharField(max_length=255)
    marketplace_id = models.CharField(max_length=255, unique=True)
    country_code = models.CharField(max_length=255)
    currency_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + f"| {self.marketplace_id}"


class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marketplace_id = models.CharField(max_length=255)
    marketplace = models.CharField(max_length=255)
    store_name = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=500)
    access_token = models.CharField(max_length=500)
    amazon_seller_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}  {self.amazon_seller_id}"

    class Meta:
        unique_together = ['user', 'marketplace_id']


class SellerCentralSale(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    child_asin = models.CharField(max_length=255)
    parent_asin = models.CharField(max_length=255)
    sales_date = models.DateField()
    units_ordered = models.IntegerField()
    ordered_product_sales = models.FloatField()
    items_ordered = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.seller.amazon_seller_id}"
