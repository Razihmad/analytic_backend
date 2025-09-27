from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marketplace_id = models.CharField(max_length=255)
    marketplace = models.CharField(max_length=255, null=True, blank=True)
    store_name = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    ads_refresh_token = models.TextField(null=True, blank=True)
    profile_id = models.CharField(max_length=255, null=True, blank=True)
    amazon_seller_id = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}  {self.amazon_seller_id}"

    class Meta:
        unique_together = ['user', 'marketplace_id', "amazon_seller_id"]


class SellerCentralSale(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    child_asin = models.CharField(max_length=255)
    parent_asin = models.CharField(max_length=255)
    sales_date = models.DateField()
    units_ordered = models.IntegerField()
    sales = models.FloatField()
    orders = models.IntegerField()
    sku = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.seller.amazon_seller_id}"

    class Meta:
        unique_together = ["seller", "child_asin", "sales_date", "sku"]


class SellerCentralTraffic(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    sessions_date = models.DateField()
    child_asin = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    browser_sessions = models.IntegerField()
    mobile_app_sessions = models.IntegerField()
    browser_page_views = models.IntegerField()
    mobile_app_page_views = models.IntegerField()
    unit_sessions_percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_sessions(self):
        return self.browser_sessions + self.mobile_app_sessions

    @property
    def total_page_views(self):
        return self.browser_page_views + self.mobile_app_page_views

    class Meta:
        unique_together = ["seller", "sessions_date", "child_asin"]


class SellerCentralReturn(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    asin = models.CharField(max_length=255)
    return_request_date = models.DateField()
    return_delivery_date = models.DateField()
    return_type = models.CharField(max_length=255)
    refund_amount = models.FloatField()
    return_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RegionDetail(models.Model):
    marketplace_id = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.marketplace_id} | {self.region}"


class SearchQueryMarketBasket(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    asin = models.CharField(max_length=255)
    purchased_with_asin = models.CharField(max_length=255)
    purchased_with_rank = models.IntegerField()
    report_period = models.CharField(max_length=255, choices=[("WEEK", "WEEK"), ("MONTH", "MONTH")])
    start_date = models.DateField()
    end_date = models.DateField()
    combination_pct = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["seller", "asin", "purchased_with_asin", "report_period"]


class AsinMapper(models.Model):
    asin = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.asin} | {self.sku} | {self.brand}"
