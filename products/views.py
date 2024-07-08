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
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from os import environ
import requests
from pprint import pprint
from datetime import datetime

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
            refresh = RefreshToken.for_user(new_user)
            response = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if 'access' in response.data and 'refresh' in response.data:
            user = self.get_user(request.data.get('email'))
            if user:
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'document_type': user.document_type,
                    'document_number': user.document_number,
                    'status': user.status,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active,
                }
                response.data['user'] = user_data
            else:
                response.data['error'] = 'User not found'
                response.status_code = status.HTTP_404_NOT_FOUND
        return response

    def get_user(self, email):
        try:
            return MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            return None
    
class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_admin = user.is_admin
        return Response({'user_id': user.id, 'user': user.email, 'is_admin': is_admin}, status=status.HTTP_200_OK)

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
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
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

class UserSalesView(generics.ListAPIView):
    serializer_class = SaleSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return SaleModel.objects.filter(user_id=user_id)

class InvoiceCreateView(generics.GenericAPIView):
    serializer_class = SaleSerializer
    
    def post(self, request):
        try:
            url = environ.get('NUBEFACT_URL')
            token = environ.get('NUBEFACT_TOKEN')
            
            invoice_data = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': 2,
                'serie': 'BBB1',
                'numero': 1,
                'sunat_transaction': 1,
                'cliente_tipo_de_documento': 1,
                'cliente_numero_de_documento': '12345678',
                'cliente_denominacion': 'TEST',
                'cliente_direccion': 'AV. TEST 123',
                'cliente_email': 'test@mail.com',
                'fecha_de_emision': datetime.now().strftime('%d-%m-%Y'),
                'moneda': 1,
                'porcentaje_de_igv': 18.0,
                'total_gravada': 100,
                'total_igv': 18,
                'total': 118,
                'detraccion': False,
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': True,
                'items': [
                    {
                        'unidad_de_medida': 'NIU',
                        'codigo': 'P001',
                        'descripcion': 'SNEAKERS',
                        'cantidad': 1,
                        'valor_unitario': 100,
                        'precio_unitario': 118,
                        'subtotal': 100,
                        'tipo_de_igv': 1,
                        'igv': 18,
                        'total': 118,
                        
                    }
                ]
            }
            
            nubefact_response = requests.post(url, headers={'Authorization': f'Bearer {token}'}, json=invoice_data)

            pprint(nubefact_response.json())
            pprint(nubefact_response.status_code)

            return Response({
                'message': 'Invoice created!'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
