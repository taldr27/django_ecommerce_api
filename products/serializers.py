from rest_framework import serializers
from .models import ProductModel, SaleModel, SaleDetailModel

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url
        
        return representation
    
class ProductUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.FloatField(required=False)
    image = serializers.ImageField(required=False)
    color = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    stock = serializers.IntegerField(required=False)
    review = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    category = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    
    class Meta:
        model = ProductModel
        fields = '__all__'

class SaleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleDetailModel
        exclude = ['sale_id']

class SaleSerializer(serializers.ModelSerializer):
    sale_details = SaleDetailSerializer(many=True)

    class Meta:
        model = SaleModel
        fields = '__all__'
