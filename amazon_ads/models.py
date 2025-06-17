from django.db import models
from amazon.models import Seller

# Create your models here.


class AmazonAdsSaleAsin(models.Model):
    amazon_ads = models.ForeignKey(Seller, on_delete=models.CASCADE)
    asin = models.CharField(max_length=255)
    sales_date = models.DateField()
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    cpc = models.DecimalField(max_digits=10, decimal_places=2)
    campaign_type = models.CharField(max_length=256, null=True, blank=True)
    campaign_name = models.CharField(max_length=256, null=True)
    campaign_id = models.CharField(max_length=256, null=True)
    orders = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['amazon_ads', 'asin', 'sales_date', "campaign_type", "campaign_id"]


class AmazonAdsSaleCampaign(models.Model):
    amazon_ads = models.ForeignKey(Seller, on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255)
    sales_date = models.DateField()
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    cpc = models.DecimalField(max_digits=10, decimal_places=2)
    campaign_bidding_strategy = models.CharField(max_length=255, null=True, blank=True)
    orders = models.IntegerField(default=0)
    campaign_status = models.CharField(max_length=255, null=True, blank=True)
    campaign_type = models.CharField(max_length=256, null=True, choices=[])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['amazon_ads', 'campaign_name', 'sales_date', "campaign_type"]


class SearchTerm(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    search_term = models.CharField(max_length=256)
    cost = models.CharField(max_length=256)
    sales = models.FloatField()
    units_sold = models.IntegerField()
    orders = models.IntegerField()
    cost = models.FloatField()
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    targeting = models.CharField(max_length=256)
    campaign_name = models.CharField(max_length=256)
    campaign_id = models.CharField(max_length=256)
    keyword = models.CharField(max_length=256)
    keyword_id = models.CharField(max_length=256)
    keyword_type = models.CharField(max_length=256)
    keyword_bid = models.CharField(max_length=256)
    ad_group_name = models.CharField(max_length=256)
    ad_group_id = models.CharField(max_length=256)
    search_term_date = models.DateField()
    match_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["seller", "search_term", "campaign_id", "search_term_date"]

    @property
    def acos(self):
        return round(self.cost / self.sales * 100, 3) if self.sales else 0

    @property
    def roas(self):
        return round(self.sales / self.cost, 3) if self.cost else 0

    @property
    def cvr(self):
        return round(self.orders / self.clicks * 100, 3) if self.clicks else 0
