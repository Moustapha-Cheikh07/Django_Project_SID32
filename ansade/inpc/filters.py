import django_filters
from .models import ProductType, Product, Wilaya, Moughata, Commune, PointOfSale, Cart, CartProduct, ProductPrice

class ProductTypeFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProductType
        fields = ['code', 'label']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['code', 'name', 'product_type']

class WilayaFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Wilaya
        fields = ['code', 'name']

class MoughataFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Moughata
        fields = ['code', 'label', 'wilaya']

class CommuneFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Commune
        fields = ['code', 'name', 'moughata']

class PointOfSaleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = PointOfSale
        fields = ['code', 'name', 'commune']

class CartFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Cart
        fields = ['code', 'name']

class CartProductFilter(django_filters.FilterSet):
    class Meta:
        model = CartProduct
        fields = ['cart', 'product']

class ProductPriceFilter(django_filters.FilterSet):
    class Meta:
        model = ProductPrice
        fields = ['product', 'point_of_sale', 'date_from', 'date_to']