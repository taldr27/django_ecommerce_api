from rest_framework import serializers
from .models import ProductModel, SaleModel, SaleDetailModel, MyUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = MyUser
        exclude = ['last_login']
        
    def save(self):
        email=self.validated_data['email']
        password=self.validated_data['password']
        name=self.validated_data['name']
        document_type=self.validated_data['document_type']
        document_number=self.validated_data['document_number']

        user = MyUser(
            name=name,
            email=email,
            document_type=document_type,
            document_number=document_number
        )
        
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
    class Meta:
        model = SaleDetailModel
        exclude = ['sale_id']

class SaleSerializer(serializers.ModelSerializer):
    sale_details = SaleDetailSerializer(many=True)

    class Meta:
        model = SaleModel
        fields = '__all__'
