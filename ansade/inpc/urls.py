from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import dashboard
from .views import (
    dashboard,
    product_inpc_line_chart,
    global_inpc_line_chart
)


urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # INPC Calculation
    path('calculate-inpc/', views.calculate_inpc, name='calculate_inpc'),
    
    # Import/Export

    path('import-export/', views.import_export_data, name='import_export_data'),
    path('download-template/<str:model_name>/', views.download_template, name='download_template'),
    
    # Filtering
    path('filter/', views.filter_data, name='filter_data'),
    
    # Administrative Structures
    path('administrative-structures/', views.administrative_structures, name='administrative_structures'),
    
    # ProductType URLs
    path('product-types/', views.ProductTypeListView.as_view(), name='product_type_list'),
    path('product-types/create/', views.ProductTypeCreateView.as_view(), name='product_type_create'),
    path('product-types/<int:pk>/update/', views.ProductTypeUpdateView.as_view(), name='product_type_update'),
    path('product-types/<int:pk>/delete/', views.ProductTypeDeleteView.as_view(), name='product_type_delete'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Wilaya URLs
    path('wilayas/', views.WilayaListView.as_view(), name='wilaya_list'),
    path('wilayas/create/', views.WilayaCreateView.as_view(), name='wilaya_create'),
    path('wilayas/<int:pk>/update/', views.WilayaUpdateView.as_view(), name='wilaya_update'),
    path('wilayas/<int:pk>/delete/', views.WilayaDeleteView.as_view(), name='wilaya_delete'),
    
    # Moughata URLs
    path('moughatas/', views.MoughataListView.as_view(), name='moughata_list'),
    path('moughatas/create/', views.MoughataCreateView.as_view(), name='moughata_create'),
    path('moughatas/<int:pk>/update/', views.MoughataUpdateView.as_view(), name='moughata_update'),
    path('moughatas/<int:pk>/delete/', views.MoughataDeleteView.as_view(), name='moughata_delete'),
    
    # Commune URLs
    path('communes/', views.CommuneListView.as_view(), name='commune_list'),
    path('communes/create/', views.CommuneCreateView.as_view(), name='commune_create'),
    path('communes/<int:pk>/update/', views.CommuneUpdateView.as_view(), name='commune_update'),
    path('communes/<int:pk>/delete/', views.CommuneDeleteView.as_view(), name='commune_delete'),
    
    # PointOfSale URLs
    path('points-of-sale/', views.PointOfSaleListView.as_view(), name='point_of_sale_list'),
    path('points-of-sale/create/', views.PointOfSaleCreateView.as_view(), name='point_of_sale_create'),
    path('points-of-sale/<int:pk>/update/', views.PointOfSaleUpdateView.as_view(), name='point_of_sale_update'),
    path('points-of-sale/<int:pk>/delete/', views.PointOfSaleDeleteView.as_view(), name='point_of_sale_delete'),
    
    # Cart URLs
    path('carts/', views.CartListView.as_view(), name='cart_list'),
    path('carts/create/', views.CartCreateView.as_view(), name='cart_create'),
    path('carts/<int:pk>/update/', views.CartUpdateView.as_view(), name='cart_update'),
    path('carts/<int:pk>/delete/', views.CartDeleteView.as_view(), name='cart_delete'),
    
    # CartProduct URLs
    path('cart-products/', views.CartProductListView.as_view(), name='cart_product_list'),
    path('cart-products/create/', views.CartProductCreateView.as_view(), name='cart_product_create'),
    path('cart-products/<int:pk>/update/', views.CartProductUpdateView.as_view(), name='cart_product_update'),
    path('cart-products/<int:pk>/delete/', views.CartProductDeleteView.as_view(), name='cart_product_delete'),
    
    # ProductPrice URLs
    path('product-prices/', views.ProductPriceListView.as_view(), name='product_price_list'),
    path('product-prices/create/', views.ProductPriceCreateView.as_view(), name='product_price_create'),
    path('product-prices/<int:pk>/update/', views.ProductPriceUpdateView.as_view(), name='product_price_update'),
    path('product-prices/<int:pk>/delete/', views.ProductPriceDeleteView.as_view(), name='product_price_delete'),

    # URLs pour l'évolution des prix
    path('price-evolution/', views.price_evolution, name='price_evolution'),
    path('price-evolution/data/', views.price_evolution_data, name='price_evolution_data'),

    # ... other URLs ...

    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/product-inpc-chart/', product_inpc_line_chart, name='product_inpc_line_chart'),
    path('dashboard/global-inpc-chart/', global_inpc_line_chart, name='global_inpc_line_chart'),



]