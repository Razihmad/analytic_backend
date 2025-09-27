from import_export import resources
from import_export.fields import Field
from .models import AsinMapper


class AsinMapperResource(resources.ModelResource):
    """Resource for importing/exporting AsinMapper data"""
    
    # Define fields for import/export
    asin = Field(attribute='asin', column_name='asin')
    title = Field(attribute='title', column_name='title')
    sku = Field(attribute='sku', column_name='sku')
    product_type = Field(attribute='product_type', column_name='product_type')
    product = Field(attribute='product', column_name='product')
    
    class Meta:
        model = AsinMapper
        fields = ('asin', 'title', 'sku', 'product_type', 'product')
        import_id_fields = ('asin', 'sku')  # Use asin and sku as unique identifiers
        skip_unchanged = True
        report_skipped = True
