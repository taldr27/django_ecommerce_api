from django.contrib.postgres.fields import ArrayField
from django.db import models
from cloudinary.models import CloudinaryField

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
