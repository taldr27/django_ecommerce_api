from django.urls import path
from .views import (
    ProductView,
    ProductCreateView,
    ProductBigCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductUploadImageView,
    SaleView,
    SaleCreateView,
    SaleUpdateView,
    SaleDeleteView,
    RegisterView,
    LoginView
)

urlpatterns = [
    path('products/all', ProductView.as_view(), name='products'),
    path('products/create', ProductCreateView.as_view(), name='product-create'),
    path('products/big-create', ProductBigCreateView.as_view(), name='product-big-create'),
    path('products/update/<int:pk>', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<int:pk>', ProductDeleteView.as_view(), name='product-delete'),
    path('products/upload-image', ProductUploadImageView.as_view(), name='product-upload-image'),
    path('sales/all', SaleView.as_view(), name='sales'),
    path('sales/create', SaleCreateView.as_view(), name='sale-create'),
    path('sales/update/<int:pk>', SaleUpdateView.as_view(), name='sale-update'),
    path('sales/delete/<int:pk>', SaleDeleteView.as_view(), name='sale-delete'),
    path('user/register', RegisterView.as_view(), name='user-register'),
    path('user/login', LoginView.as_view(), name='user-login')
]
