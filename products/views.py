from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ProductSerializer, ProductModel, ProductUpdateSerializer, SaleModel, SaleSerializer, SaleDetailSerializer, SaleDetailModel, UserCreateSerializer, MyTokenObtainPairSerializer
from .models import MyUser
from cloudinary.uploader import upload
from django.http import Http404
from pprint import pprint
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class RegisterView(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserCreateSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = MyUser.objects.filter(email=email).first()
            
            if user:
                return Response({'error': 'User already exists!'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_user = serializer.save()
            response = self.serializer_class(new_user).data
            
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ProductView(generics.ListAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset:
            return Response({'message': 'No products found!'}, status=status.HTTP_404_NOT_FOUND)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductCreateView(generics.CreateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    
class ProductBigCreateView(generics.CreateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductUpdateView(generics.UpdateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductUpdateSerializer
    
class ProductDeleteView(generics.DestroyAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.stock -= 1
            instance.save()
            return Response({'message': 'Product deleted!'}, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductUploadImageView(generics.GenericAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')
            
            if not image_file:
                return Response({'error': 'No image uploaded!'}, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_image = upload(image_file)
            
            return Response({'message': 'Image uploaded!', 'image_url': uploaded_image['url']}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SaleView(generics.ListAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer

class SaleCreateView(generics.CreateAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            
            user = MyUser.objects.get(id=data['user_id'])
            
            sale = SaleModel.objects.create(
                total_price=data['total_price'],
                user_id=user,
            )
            sale.save()
            
            for item in data['sale_details']:
                product_id = item['product_id']
                quantity = item['quantity']
                
                product = ProductModel.objects.get(id=product_id)
                if product.stock < quantity:
                    raise Exception(f'Product {product.name} has insufficient stock in the store!')
                
                product.stock -= quantity
                product.save()
                
                sale_detail = SaleDetailModel.objects.create(
                    quantity=quantity,
                    price=item['price'],
                    subtotal=item['subtotal'],
                    product_id=product,
                    sale_id=sale
                )
                
                sale_detail.save()
                
            return Response({'message': 'Sale created!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SaleUpdateView(generics.UpdateAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer
    
class SaleDeleteView(generics.DestroyAPIView):
    queryset = SaleModel.objects.all()
    serializer_class = SaleSerializer
