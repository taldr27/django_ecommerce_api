from django.contrib.postgres.fields import ArrayField
from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User

class ProductModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image')
    color = ArrayField(models.CharField(max_length=10, null=True), default=list, blank=True)
    stock = models.IntegerField()
    review = ArrayField(models.CharField(max_length=200, null=True), default=list, blank=True)
    category = ArrayField(models.CharField(max_length=20, null=True), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

class SaleModel(models.Model):
    id = models.AutoField(primary_key=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales'

    def __str__(self):
        return self.product.name

class SaleDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    product_id = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    sale_id = models.ForeignKey(SaleModel, on_delete=models.CASCADE, related_name='sale_details')
    
    class Meta:
      db_table = 'sale_details'
    
    def __str__(self):
        return self.id
