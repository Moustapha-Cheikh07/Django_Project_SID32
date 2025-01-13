# inpc/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Accueil
    path('', views.home, name='home'),

    # ProductType URLs
    path('product-types/', views.ProductTypeListView.as_view(), name='product_type_list'),
    path('product-types/create/', views.ProductTypeCreateView.as_view(), name='product_type_create'),
    path('product-types/update/<int:pk>/', views.ProductTypeUpdateView.as_view(), name='product_type_update'),
    path('product-types/delete/<int:pk>/', views.ProductTypeDeleteView.as_view(), name='product_type_delete'),

    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/update/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Wilaya URLs
    path('wilayas/', views.WilayaListView.as_view(), name='wilaya_list'),
    path('wilayas/create/', views.WilayaCreateView.as_view(), name='wilaya_create'),
    path('wilayas/update/<int:pk>/', views.WilayaUpdateView.as_view(), name='wilaya_update'),
    path('wilayas/delete/<int:pk>/', views.WilayaDeleteView.as_view(), name='wilaya_delete'),

    # Moughata URLs
    path('moughatas/', views.MoughataListView.as_view(), name='moughata_list'),
    path('moughatas/create/', views.MoughataCreateView.as_view(), name='moughata_create'),
    path('moughatas/update/<int:pk>/', views.MoughataUpdateView.as_view(), name='moughata_update'),
    path('moughatas/delete/<int:pk>/', views.MoughataDeleteView.as_view(), name='moughata_delete'),

    # Commune URLs
    path('communes/', views.CommuneListView.as_view(), name='commune_list'),
    path('communes/create/', views.CommuneCreateView.as_view(), name='commune_create'),
    path('communes/update/<int:pk>/', views.CommuneUpdateView.as_view(), name='commune_update'),
    path('communes/delete/<int:pk>/', views.CommuneDeleteView.as_view(), name='commune_delete'),

    # PointOfSale URLs
    path('points-of-sale/', views.PointOfSaleListView.as_view(), name='point_of_sale_list'),
    path('points-of-sale/create/', views.PointOfSaleCreateView.as_view(), name='point_of_sale_create'),
    path('points-of-sale/update/<int:pk>/', views.PointOfSaleUpdateView.as_view(), name='point_of_sale_update'),
    path('points-of-sale/delete/<int:pk>/', views.PointOfSaleDeleteView.as_view(), name='point_of_sale_delete'),

    # Cart URLs
    path('carts/', views.CartListView.as_view(), name='cart_list'),
    path('carts/create/', views.CartCreateView.as_view(), name='cart_create'),
    path('carts/update/<int:pk>/', views.CartUpdateView.as_view(), name='cart_update'),
    path('carts/delete/<int:pk>/', views.CartDeleteView.as_view(), name='cart_delete'),

    # CartProduct URLs
    path('cart-products/', views.CartProductListView.as_view(), name='cart_product_list'),
    path('cart-products/create/', views.CartProductCreateView.as_view(), name='cart_product_create'),
    path('cart-products/update/<int:pk>/', views.CartProductUpdateView.as_view(), name='cart_product_update'),
    path('cart-products/delete/<int:pk>/', views.CartProductDeleteView.as_view(), name='cart_product_delete'),

    # ProductPrice URLs
    path('product-prices/', views.ProductPriceListView.as_view(), name='product_price_list'),
    path('product-prices/create/', views.ProductPriceCreateView.as_view(), name='product_price_create'),
    path('product-prices/update/<int:pk>/', views.ProductPriceUpdateView.as_view(), name='product_price_update'),
    path('product-prices/delete/<int:pk>/', views.ProductPriceDeleteView.as_view(), name='product_price_delete'),
]