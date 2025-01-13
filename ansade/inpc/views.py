from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import ProductType, Product, Wilaya, Moughata, Commune, PointOfSale, Cart, CartProduct, ProductPrice
from .forms import ProductTypeForm, ProductForm, WilayaForm, MoughataForm, CommuneForm, PointOfSaleForm, CartForm, CartProductForm, ProductPriceForm

def home(request):
    return render(request, 'inpc/home.html')

# ProductType Views
class ProductTypeListView(ListView):
    model = ProductType
    template_name = 'inpc/product_type_list.html'
    context_object_name = 'product_types'

class ProductTypeCreateView(CreateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = 'inpc/product_type_form.html'
    success_url = reverse_lazy('product_type_list')

class ProductTypeUpdateView(UpdateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = 'inpc/product_type_form.html'
    success_url = reverse_lazy('product_type_list')

class ProductTypeDeleteView(DeleteView):
    model = ProductType
    template_name = 'inpc/product_type_confirm_delete.html'
    success_url = reverse_lazy('product_type_list')

# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'inpc/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inpc/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inpc/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'inpc/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# Wilaya Views
class WilayaListView(ListView):
    model = Wilaya
    template_name = 'inpc/wilaya_list.html'
    context_object_name = 'wilayas'

class WilayaCreateView(CreateView):
    model = Wilaya
    form_class = WilayaForm
    template_name = 'inpc/wilaya_form.html'
    success_url = reverse_lazy('wilaya_list')

class WilayaUpdateView(UpdateView):
    model = Wilaya
    form_class = WilayaForm
    template_name = 'inpc/wilaya_form.html'
    success_url = reverse_lazy('wilaya_list')

class WilayaDeleteView(DeleteView):
    model = Wilaya
    template_name = 'inpc/wilaya_confirm_delete.html'
    success_url = reverse_lazy('wilaya_list')

# Moughata Views
class MoughataListView(ListView):
    model = Moughata
    template_name = 'inpc/moughata_list.html'
    context_object_name = 'moughatas'

class MoughataCreateView(CreateView):
    model = Moughata
    form_class = MoughataForm
    template_name = 'inpc/moughata_form.html'
    success_url = reverse_lazy('moughata_list')

class MoughataUpdateView(UpdateView):
    model = Moughata
    form_class = MoughataForm
    template_name = 'inpc/moughata_form.html'
    success_url = reverse_lazy('moughata_list')

class MoughataDeleteView(DeleteView):
    model = Moughata
    template_name = 'inpc/moughata_confirm_delete.html'
    success_url = reverse_lazy('moughata_list')

# Commune Views
class CommuneListView(ListView):
    model = Commune
    template_name = 'inpc/commune_list.html'
    context_object_name = 'communes'

class CommuneCreateView(CreateView):
    model = Commune
    form_class = CommuneForm
    template_name = 'inpc/commune_form.html'
    success_url = reverse_lazy('commune_list')

class CommuneUpdateView(UpdateView):
    model = Commune
    form_class = CommuneForm
    template_name = 'inpc/commune_form.html'
    success_url = reverse_lazy('commune_list')

class CommuneDeleteView(DeleteView):
    model = Commune
    template_name = 'inpc/commune_confirm_delete.html'
    success_url = reverse_lazy('commune_list')

# PointOfSale Views
class PointOfSaleListView(ListView):
    model = PointOfSale
    template_name = 'inpc/point_of_sale_list.html'
    context_object_name = 'points_of_sale'

class PointOfSaleCreateView(CreateView):
    model = PointOfSale
    form_class = PointOfSaleForm
    template_name = 'inpc/point_of_sale_form.html'
    success_url = reverse_lazy('point_of_sale_list')

class PointOfSaleUpdateView(UpdateView):
    model = PointOfSale
    form_class = PointOfSaleForm
    template_name = 'inpc/point_of_sale_form.html'
    success_url = reverse_lazy('point_of_sale_list')

class PointOfSaleDeleteView(DeleteView):
    model = PointOfSale
    template_name = 'inpc/point_of_sale_confirm_delete.html'
    success_url = reverse_lazy('point_of_sale_list')

# Cart Views
class CartListView(ListView):
    model = Cart
    template_name = 'inpc/cart_list.html'
    context_object_name = 'carts'

class CartCreateView(CreateView):
    model = Cart
    form_class = CartForm
    template_name = 'inpc/cart_form.html'
    success_url = reverse_lazy('cart_list')

class CartUpdateView(UpdateView):
    model = Cart
    form_class = CartForm
    template_name = 'inpc/cart_form.html'
    success_url = reverse_lazy('cart_list')

class CartDeleteView(DeleteView):
    model = Cart
    template_name = 'inpc/cart_confirm_delete.html'
    success_url = reverse_lazy('cart_list')

# CartProduct Views
class CartProductListView(ListView):
    model = CartProduct
    template_name = 'inpc/cart_product_list.html'
    context_object_name = 'cart_products'

class CartProductCreateView(CreateView):
    model = CartProduct
    form_class = CartProductForm
    template_name = 'inpc/cart_product_form.html'
    success_url = reverse_lazy('cart_product_list')

class CartProductUpdateView(UpdateView):
    model = CartProduct
    form_class = CartProductForm
    template_name = 'inpc/cart_product_form.html'
    success_url = reverse_lazy('cart_product_list')

class CartProductDeleteView(DeleteView):
    model = CartProduct
    template_name = 'inpc/cart_product_confirm_delete.html'
    success_url = reverse_lazy('cart_product_list')

# ProductPrice Views
class ProductPriceListView(ListView):
    model = ProductPrice
    template_name = 'inpc/product_price_list.html'
    context_object_name = 'product_prices'

class ProductPriceCreateView(CreateView):
    model = ProductPrice
    form_class = ProductPriceForm
    template_name = 'inpc/product_price_form.html'
    success_url = reverse_lazy('product_price_list')

class ProductPriceUpdateView(UpdateView):
    model = ProductPrice
    form_class = ProductPriceForm
    template_name = 'inpc/product_price_form.html'
    success_url = reverse_lazy('product_price_list')

class ProductPriceDeleteView(DeleteView):
    model = ProductPrice
    template_name = 'inpc/product_price_confirm_delete.html'
    success_url = reverse_lazy('product_price_list')