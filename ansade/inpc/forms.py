from django import forms
from .models import ProductType, Product, Wilaya, Moughata, Commune, PointOfSale, Cart, CartProduct, ProductPrice
from django.core.validators import MinValueValidator, MaxValueValidator

class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})

class ProductTypeForm(BaseModelForm):
    class Meta:
        model = ProductType
        fields = ['code', 'label', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Description du type de produit'})
        }

class ProductForm(BaseModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'unit_measure', 'product_type']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Description du produit'}),
            'unit_measure': forms.TextInput(attrs={'placeholder': 'Ex: kg, l, unité'})
        }

class WilayaForm(BaseModelForm):
    class Meta:
        model = Wilaya
        fields = ['code', 'name']

class MoughataForm(BaseModelForm):
    class Meta:
        model = Moughata
        fields = ['code', 'label', 'wilaya']

class CommuneForm(BaseModelForm):
    class Meta:
        model = Commune
        fields = ['code', 'name', 'moughata']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'moughata' in self.fields:
            self.fields['moughata'].queryset = Moughata.objects.all().order_by('wilaya__name', 'label')

class PointOfSaleForm(BaseModelForm):
    class Meta:
        model = PointOfSale
        fields = ['code', 'name', 'gps_lat', 'gps_lon', 'commune']
        widgets = {
            'gps_lat': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Latitude'}),
            'gps_lon': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Longitude'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'commune' in self.fields:
            self.fields['commune'].queryset = Commune.objects.all().order_by('moughata__wilaya__name', 'name')

class CartForm(BaseModelForm):
    class Meta:
        model = Cart
        fields = ['code', 'name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Description du panier'})
        }

class CartProductForm(BaseModelForm):
    class Meta:
        model = CartProduct
        fields = ['product', 'cart', 'weight', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        
        return cleaned_data

class ProductPriceForm(BaseModelForm):
    class Meta:
        model = ProductPrice
        fields = ['product', 'point_of_sale', 'value', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
            'value': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        value = cleaned_data.get('value')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        
        if value and value < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        
        return cleaned_data

class ImportForm(forms.Form):
    model_choice = forms.ChoiceField(
        choices=[
            ('ProductType', 'Type de Produit'),
            ('Product', 'Produit'),
            ('Wilaya', 'Wilaya'),
            ('Moughata', 'Moughata'),
            ('Commune', 'Commune'),
            ('PointOfSale', 'Point de Vente'),
            ('Cart', 'Panier'),
            ('CartProduct', 'Produit du Panier'),
            ('ProductPrice', 'Prix du Produit'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Fichier Excel (.xlsx, .xls)'
    )