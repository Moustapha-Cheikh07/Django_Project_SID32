from django import forms
from .models import ProductType, Product, Wilaya, Moughata, Commune, PointOfSale, Cart, CartProduct, ProductPrice

class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['code', 'label', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'unit_measure', 'product_type']

class WilayaForm(forms.ModelForm):
    class Meta:
        model = Wilaya
        fields = ['code', 'name']

class MoughataForm(forms.ModelForm):
    class Meta:
        model = Moughata
        fields = ['code', 'label', 'wilaya']

class CommuneForm(forms.ModelForm):
    class Meta:
        model = Commune
        fields = ['code', 'name', 'moughata']

class PointOfSaleForm(forms.ModelForm):
    class Meta:
        model = PointOfSale
        fields = ['code', 'name', 'gps_lat', 'gps_lon', 'commune']

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['code', 'name', 'description']

class CartProductForm(forms.ModelForm):
    class Meta:
        model = CartProduct
        fields = ['product', 'cart', 'weight', 'date_from', 'date_to']

class ProductPriceForm(forms.ModelForm):
    class Meta:
        model = ProductPrice
        fields = ['product', 'point_of_sale', 'value', 'date_from', 'date_to']