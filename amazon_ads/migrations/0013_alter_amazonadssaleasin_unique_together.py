from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amazon_ads', '0012_searchterm_orders'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='amazonadssaleasin',
            unique_together={('amazon_ads', 'asin', 'sales_date', 'campaign_type', 'campaign_id')},
        ),
    ]
