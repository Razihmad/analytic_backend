
from amazon.serializers import process_total_and_sales_data

from django.test import TestCase


class UnitTestCases(TestCase):

    def test_process_total_and_sales_data(self):
        # Test case 1: Basic test with sample data
        total_sales = [
            {
                "ordered_product_sales": 100,
                "items_ordered": 2,
                "units_ordered": 3
            },
            {
                "ordered_product_sales": 200,
                "items_ordered": 4,
                "units_ordered": 5
            }
        ]

        ads_sale = [
            {
                "sales": 150,
                "spend": 50
            },
            {
                "sales": 100,
                "spend": 30
            }
        ]

        result = process_total_and_sales_data(total_sales=total_sales, ads_sale=ads_sale)

        assert result["total_revenue"] == 300
        assert result["ads_revenue"] == 250
        assert result["organic_revenue"] == 50
        assert result["total_orders"] == 6
        assert result["total_units"] == 8
        assert result["total_aov"] == 50
        assert result["ads_spend"] == 80
        assert result["tacos"] == 0
        assert result["acos"] == 0
        assert result["ads_roas"] == 3
        assert result["total_roas"] == 3

        # Test case 2: Empty data
        result = process_total_and_sales_data(total_sales=[], ads_sale=[])
        assert result["total_revenue"] == 0
        assert result["ads_revenue"] == 0
        assert result["organic_revenue"] == 0

        # Test case 3: Zero division handling
        total_sales = [
            {
                "ordered_product_sales": 0,
                "items_ordered": 0,
                "units_ordered": 0
            }
        ]
        ads_sale = [
            {
                "sales": 0,
                "spend": 0
            }
        ]

        result = process_total_and_sales_data(total_sales=total_sales, ads_sale=ads_sale)
        assert result["total_revenue"] == 0
        assert result["total_aov"] == 0
        assert result["tacos"] == 0
        assert result["acos"] == 0
        assert result["ads_roas"] == 0
        assert result["total_roas"] == 0
