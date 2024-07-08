from rest_framework import serializers
from .models import ProductModel, SaleModel, SaleDetailModel, MyUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserCreateSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(default=False)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = MyUser
        exclude = ['last_login']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        is_admin = validated_data.pop('is_admin', False)
        user = MyUser.objects.create(**validated_data, is_admin=is_admin)
        user.set_password(password)
        user.save()
        return user
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

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
    product = ProductSerializer(read_only=True, source='product_id')

    class Meta:
        model = SaleDetailModel
        fields = ['id', 'quantity', 'price', 'subtotal', 'product']

class SaleSerializer(serializers.ModelSerializer):
    sale_details = SaleDetailSerializer(many=True)

    class Meta:
        model = SaleModel
        fields = '__all__'

class SaleDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleDetailModel
        exclude = ['sale_id']

class SaleCreateSerializer(serializers.ModelSerializer):
    sale_details = SaleDetailCreateSerializer(source='saleDetails', many=True)

    class Meta:
        model = SaleModel
        fields = '__all__'
