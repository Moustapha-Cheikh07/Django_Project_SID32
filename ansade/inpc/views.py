from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.apps import apps
from .models import *
from .forms import *
from .filters import *
from datetime import datetime, timedelta
import pandas as pd
import io
import xlsxwriter
from django.db.models import Avg
from dateutil.relativedelta import relativedelta
@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Calculer l'INPC pour les 4 derniers mois
    inpc_last_4_months = []
    aujourdhui = datetime.today()

    for i in range(4):
        date = aujourdhui - relativedelta(months=i)
        mois = date.month
        annee = date.year

        # Calculer l'INPC pour ce mois
        valeur_inpc = calculate_inpc_for_date(datetime(annee, mois, 1))
        inpc_last_4_months.append({
            'month': mois,  # Assurez-vous que les clés correspondent à celles utilisées dans le template
            'year': annee,
            'inpc': valeur_inpc
        })

    # Ajouter les données au contexte
    context = {
        'total_products': Product.objects.count(),
        'total_points_of_sale': PointOfSale.objects.count(),
        'total_carts': Cart.objects.count(),
        'inpc_last_4_months': inpc_last_4_months,  # Assurez-vous que la clé correspond à celle utilisée dans le template
    }
    return render(request, 'inpc/home.html', context)


def calculate_inpc_for_date(date):
    """
    Fonction utilitaire pour calculer l'INPC pour une date donnée.
    """
    # Calculer le prix moyen de chaque produit pour la période donnée
    product_avg_prices = {}
    for product in Product.objects.all():
        # Récupérer les prix du produit dans tous les points de vente pour la période donnée
        avg_price = ProductPrice.objects.filter(
            product=product,
            date_from__lte=date,
            date_to__gte=date
        ).aggregate(Avg('value'))['value__avg']

        if avg_price is not None:
            product_avg_prices[product.id] = avg_price

    # Si aucun prix n'est trouvé, retourner 0
    if not product_avg_prices:
        return 0

    # Calculer l'INPC pour chaque panier
    cart_inpc = {}
    for cart in Cart.objects.all():
        total_weighted_price = 0
        total_weight = 0

        # Récupérer les produits du panier pour la période donnée
        cart_products = CartProduct.objects.filter(
            cart=cart,
            date_from__lte=date,
            date_to__gte=date
        )

        for cart_product in cart_products:
            product_id = cart_product.product.id
            if product_id in product_avg_prices:
                total_weighted_price += product_avg_prices[product_id] * cart_product.weight
                total_weight += cart_product.weight

        # Calculer l'INPC du panier
        if total_weight > 0:
            cart_inpc[cart.id] = total_weighted_price / total_weight
        else:
            cart_inpc[cart.id] = 0

    # Si aucun panier n'est trouvé, retourner 0
    if not cart_inpc:
        return 0

    # Calculer l'INPC global
    return sum(cart_inpc.values()) / len(cart_inpc)
@login_required
def calculate_inpc(request):
    """
    Vue Django pour calculer l'INPC en fonction des données soumises par l'utilisateur.
    """
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            date = datetime(year, month, 1)  # Créer un objet datetime pour le début du mois

            # Année de base (2019)
            base_year = 2019
            base_date = datetime(base_year, 1, 1)

            # Calculer l'INPC global pour l'année de base (2019)
            base_inpc = calculate_inpc_for_date(base_date)

            # Calculer l'INPC global pour la période donnée
            current_inpc = calculate_inpc_for_date(date)

            # Normaliser l'INPC global par rapport à l'année de base
            if base_inpc > 0:
                inpc_global = (current_inpc / base_inpc) * 100  # Base 100 = 2019
            else:
                inpc_global = 0

            # Préparer le contexte pour le template
            context = {
                'inpc': inpc_global,
                'month': month,
                'year': year,
            }
            return render(request, 'inpc/inpc_result.html', context)

        except Exception as e:
            messages.error(request, f"Erreur lors du calcul de l'INPC : {str(e)}")
            return redirect('calculate_inpc')

    # Si la méthode n'est pas POST, afficher le formulaire
    current_year = datetime.now().year
    return render(request, 'inpc/inpc_form.html', {'current_year': current_year})

@login_required
def import_export_data(request):
    models = [
        {"name": "ProductType", "verbose_name": "Type de Produit"},
        {"name": "Product", "verbose_name": "Produit"},
        {"name": "Wilaya", "verbose_name": "Wilaya"},
        {"name": "Moughata", "verbose_name": "Moughata"},
        {"name": "Commune", "verbose_name": "Commune"},
        {"name": "PointOfSale", "verbose_name": "Point de Vente"},
        {"name": "Cart", "verbose_name": "Panier"},
        {"name": "CartProduct", "verbose_name": "Produit du Panier"},
        {"name": "ProductPrice", "verbose_name": "Prix du Produit"},
    ]
    
    if request.method == 'POST':
        model_name = request.POST.get('model')
        action = request.POST.get('action')
        
        model = next((m for m in models if m['name'].lower() == model_name.lower()), None)
        if model:
            model_class = globals()[model['name']]
            if action == 'import':
                return import_data(request, model_class)
            elif action == 'export':
                return export_data(request, model_class)
        
        messages.error(request, "Modèle invalide sélectionné.")
    
    context = {
        'models': models
    }
    return render(request, 'inpc/import_export.html', context)

def import_data(request, model):
    if 'file' not in request.FILES:
        messages.error(request, "Veuillez fournir un fichier Excel.")
        return redirect('import_export_data')
    
    excel_file = request.FILES['file']
    
    try:
        df = pd.read_excel(excel_file)
        
        for _, row in df.iterrows():
            data = row.to_dict()
            
            # Handle foreign key relationships
            if model == Product:
                product_type = ProductType.objects.get(code=data['product_type'])
                data['product_type'] = product_type
            elif model == Moughata:
                wilaya = Wilaya.objects.get(code=data['wilaya'])
                data['wilaya'] = wilaya
            elif model == Commune:
                moughata = Moughata.objects.get(code=data['moughata'])
                data['moughata'] = moughata
            elif model == PointOfSale:
                commune = Commune.objects.get(code=data['commune'])
                data['commune'] = commune
            elif model == CartProduct:
                product = Product.objects.get(code=data['product'])
                cart = Cart.objects.get(code=data['cart'])
                data['product'] = product
                data['cart'] = cart
            elif model == ProductPrice:
                product = Product.objects.get(code=data['product'])
                point_of_sale = PointOfSale.objects.get(code=data['point_of_sale'])
                data['product'] = product
                data['point_of_sale'] = point_of_sale
            
            model.objects.create(**data)
        
        messages.success(request, f"Données importées avec succès pour {model.__name__}")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'importation : {str(e)}")
    
    return redirect('import_export_data')

def export_data(request, model):
    # Récupérer les objets du modèle
    queryset = model.objects.all()
    
    # Préparer les données à exporter
    data = []
    for obj in queryset:
        item = {}
        for field in obj._meta.fields:
            if field.is_relation:
                # Gérer les relations pour inclure le code ou une autre valeur représentative
                related_obj = getattr(obj, field.name, None)
                item[field.name] = related_obj.code if related_obj else None
            else:
                item[field.name] = getattr(obj, field.name)
        data.append(item)
    
    # Créer un DataFrame pandas
    df = pd.DataFrame(data)
    
    # Écrire les données dans un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # Préparer la réponse HTTP avec le fichier Excel
    output.seek(0)  # Réinitialiser le pointeur du buffer
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model.__name__}_export.xlsx'
    
    return response


@login_required
def download_template(request, model_name):
    models = [ProductType, Product, Wilaya, Moughata, Commune, PointOfSale, Cart, CartProduct, ProductPrice]
    model = next((m for m in models if m.__name__.lower() == model_name.lower()), None)
    
    if not model:
        messages.error(request, "Modèle invalide")
        return redirect('import_export_data')

    fields = [field.name for field in model._meta.fields if field.name != 'id']
    df = pd.DataFrame(columns=fields)
    
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model.__name__}_template.xlsx'
    
    return response



@login_required
def filter_data(request):
    selected_model = request.GET.get('model', 'ProductType')
    selected_column = request.GET.get('column', None)
    filter_value = request.GET.get('filter_value', None)
    
    filter_classes = {
        'ProductType': ProductTypeFilter,
        'Product': ProductFilter,
        'Wilaya': WilayaFilter,
        'Moughata': MoughataFilter,
        'Commune': CommuneFilter,
        'PointOfSale': PointOfSaleFilter,
        'Cart': CartFilter,
        'CartProduct': CartProductFilter,
        'ProductPrice': ProductPriceFilter,
    }
    
    model_class = apps.get_model('inpc', selected_model)
    filter_class = filter_classes.get(selected_model)
    
    if not filter_class:
        messages.error(request, 'Modèle non trouvé')
        return redirect('home')
    
    queryset = model_class.objects.all()
    filterset = filter_class(request.GET, queryset=queryset)
    
    # Gérer le filtrage par colonne si une colonne et une valeur de filtre sont fournies
    if selected_column and filter_value:
        try:
            queryset = queryset.filter(**{selected_column: filter_value})
        except Exception as e:
            messages.error(request, f"Erreur de filtrage : {str(e)}")
    
    field_names = [field.name for field in model_class._meta.fields]
    
    context = {
        'models': filter_classes.keys(),
        'selected_model': selected_model,
        'filter': filterset,
        'filtered_data': queryset,
        'field_names': field_names,
        'selected_column': selected_column,
        'filter_value': filter_value,
    }
    
    return render(request, 'inpc/filter_page.html', context)





@login_required
def administrative_structures(request):
    wilayas = Wilaya.objects.all()
    moughatas = Moughata.objects.all()
    communes = Commune.objects.all()

    context = {
        'wilayas': wilayas,
        'moughatas': moughatas,
        'communes': communes,
    }
    return render(request, 'inpc/administrative_structures.html', context)

# Generic views for CRUD operations

class ProductTypeListView(LoginRequiredMixin, ListView):
    model = ProductType
    template_name = 'inpc/product_type_list.html'
    context_object_name = 'product_types'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductTypeFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ProductTypeCreateView(LoginRequiredMixin, CreateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = 'inpc/product_type_form.html'
    success_url = reverse_lazy('product_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Type de produit créé avec succès.")
        return super().form_valid(form)

class ProductTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = 'inpc/product_type_form.html'
    success_url = reverse_lazy('product_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Type de produit mis à jour avec succès.")
        return super().form_valid(form)

class ProductTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductType
    template_name = 'inpc/product_type_confirm_delete.html'
    success_url = reverse_lazy('product_type_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Type de produit supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inpc/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inpc/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, "Produit créé avec succès.")
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inpc/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, "Produit mis à jour avec succès.")
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inpc/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Produit supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class WilayaListView(LoginRequiredMixin, ListView):
    model = Wilaya
    template_name = 'inpc/wilaya_list.html'
    context_object_name = 'wilayas'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = WilayaFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class WilayaCreateView(LoginRequiredMixin, CreateView):
    model = Wilaya
    form_class = WilayaForm
    template_name = 'inpc/wilaya_form.html'
    success_url = reverse_lazy('wilaya_list')

    def form_valid(self, form):
        messages.success(self.request, "Wilaya créée avec succès.")
        return super().form_valid(form)

class WilayaUpdateView(LoginRequiredMixin, UpdateView):
    model = Wilaya
    form_class = WilayaForm
    template_name = 'inpc/wilaya_form.html'
    success_url = reverse_lazy('wilaya_list')

    def form_valid(self, form):
        messages.success(self.request, "Wilaya mise à jour avec succès.")
        return super().form_valid(form)

class WilayaDeleteView(LoginRequiredMixin, DeleteView):
    model = Wilaya
    template_name = 'inpc/wilaya_confirm_delete.html'
    success_url = reverse_lazy('wilaya_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Wilaya supprimée avec succès.")
        return super().delete(request, *args, **kwargs)

class MoughataListView(LoginRequiredMixin, ListView):
    model = Moughata
    template_name = 'inpc/moughata_list.html'
    context_object_name = 'moughatas'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = MoughataFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class MoughataCreateView(LoginRequiredMixin, CreateView):
    model = Moughata
    form_class = MoughataForm
    template_name = 'inpc/moughata_form.html'
    success_url = reverse_lazy('moughata_list')

    def form_valid(self, form):
        messages.success(self.request, "Moughata créée avec succès.")
        return super().form_valid(form)

class MoughataUpdateView(LoginRequiredMixin, UpdateView):
    model = Moughata
    form_class = MoughataForm
    template_name = 'inpc/moughata_form.html'
    success_url = reverse_lazy('moughata_list')

    def form_valid(self, form):
        messages.success(self.request, "Moughata mise à jour avec succès.")
        return super().form_valid(form)

class MoughataDeleteView(LoginRequiredMixin, DeleteView):
    model = Moughata
    template_name = 'inpc/moughata_confirm_delete.html'
    success_url = reverse_lazy('moughata_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Moughata supprimée avec succès.")
        return super().delete(request, *args, **kwargs)

class CommuneListView(LoginRequiredMixin, ListView):
    model = Commune
    template_name = 'inpc/commune_list.html'
    context_object_name = 'communes'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = CommuneFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class CommuneCreateView(LoginRequiredMixin, CreateView):
    model = Commune
    form_class = CommuneForm
    template_name = 'inpc/commune_form.html'
    success_url = reverse_lazy('commune_list')

    def form_valid(self, form):
        messages.success(self.request, "Commune créée avec succès.")
        return super().form_valid(form)

class CommuneUpdateView(LoginRequiredMixin, UpdateView):
    model = Commune
    form_class = CommuneForm
    template_name = 'inpc/commune_form.html'
    success_url = reverse_lazy('commune_list')

    def form_valid(self, form):
        messages.success(self.request, "Commune mise à jour avec succès.")
        return super().form_valid(form)

class CommuneDeleteView(LoginRequiredMixin, DeleteView):
    model = Commune
    template_name = 'inpc/commune_confirm_delete.html'
    success_url = reverse_lazy('commune_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Commune supprimée avec succès.")
        return super().delete(request, *args, **kwargs)

class PointOfSaleListView(LoginRequiredMixin, ListView):
    model = PointOfSale
    template_name = 'inpc/point_of_sale_list.html'
    context_object_name = 'points_of_sale'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PointOfSaleFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class PointOfSaleCreateView(LoginRequiredMixin, CreateView):
    model = PointOfSale
    form_class = PointOfSaleForm
    template_name = 'inpc/point_of_sale_form.html'
    success_url = reverse_lazy('point_of_sale_list')

    def form_valid(self, form):
        messages.success(self.request, "Point de vente créé avec succès.")
        return super().form_valid(form)

class PointOfSaleUpdateView(LoginRequiredMixin, UpdateView):
    model = PointOfSale
    form_class = PointOfSaleForm
    template_name = 'inpc/point_of_sale_form.html'
    success_url = reverse_lazy('point_of_sale_list')

    def form_valid(self, form):
        messages.success(self.request, "Point de vente mis à jour avec succès.")
        return super().form_valid(form)

class PointOfSaleDeleteView(LoginRequiredMixin, DeleteView):
    model = PointOfSale
    template_name = 'inpc/point_of_sale_confirm_delete.html'
    success_url = reverse_lazy('point_of_sale_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Point de vente supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'inpc/cart_list.html'
    context_object_name = 'carts'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = CartFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class CartCreateView(LoginRequiredMixin, CreateView):
    model = Cart
    form_class = CartForm
    template_name = 'inpc/cart_form.html'
    success_url = reverse_lazy('cart_list')

    def form_valid(self, form):
        messages.success(self.request, "Panier créé avec succès.")
        return super().form_valid(form)

class CartUpdateView(LoginRequiredMixin, UpdateView):
    model = Cart
    form_class = CartForm
    template_name = 'inpc/cart_form.html'
    success_url = reverse_lazy('cart_list')

    def form_valid(self, form):
        messages.success(self.request, "Panier mis à jour avec succès.")
        return super().form_valid(form)

class CartDeleteView(LoginRequiredMixin, DeleteView):
    model = Cart
    template_name = 'inpc/cart_confirm_delete.html'
    success_url = reverse_lazy('cart_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Panier supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class CartProductListView(LoginRequiredMixin, ListView):
    model = CartProduct
    template_name = 'inpc/cart_product_list.html'
    context_object_name = 'cart_products'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = CartProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class CartProductCreateView(LoginRequiredMixin, CreateView):
    model = CartProduct
    form_class = CartProductForm
    template_name = 'inpc/cart_product_form.html'
    success_url = reverse_lazy('cart_product_list')

    def form_valid(self, form):
        messages.success(self.request, "Produit du panier créé avec succès.")
        return super().form_valid(form)

class CartProductUpdateView(LoginRequiredMixin, UpdateView):
    model = CartProduct
    form_class = CartProductForm
    template_name = 'inpc/cart_product_form.html'
    success_url = reverse_lazy('cart_product_list')

    def form_valid(self, form):
        messages.success(self.request, "Produit du panier mis à jour avec succès.")
        return super().form_valid(form)

class CartProductDeleteView(LoginRequiredMixin, DeleteView):
    model = CartProduct
    template_name = 'inpc/cart_product_confirm_delete.html'
    success_url = reverse_lazy('cart_product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Produit du panier supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

class ProductPriceListView(LoginRequiredMixin, ListView):
    model = ProductPrice
    template_name = 'inpc/product_price_list.html'
    context_object_name = 'product_prices'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductPriceFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ProductPriceCreateView(LoginRequiredMixin, CreateView):
    model = ProductPrice
    form_class = ProductPriceForm
    template_name = 'inpc/product_price_form.html'
    success_url = reverse_lazy('product_price_list')

    def form_valid(self, form):
        messages.success(self.request, "Prix du produit créé avec succès.")
        return super().form_valid(form)

class ProductPriceUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductPrice
    form_class = ProductPriceForm
    template_name = 'inpc/product_price_form.html'
    success_url = reverse_lazy('product_price_list')

    def form_valid(self, form):
        messages.success(self.request, "Prix du produit mis à jour avec succès.")
        return super().form_valid(form)

class ProductPriceDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductPrice
    template_name = 'inpc/product_price_confirm_delete.html'
    success_url = reverse_lazy('product_price_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Prix du produit supprimé avec succès.")
        return super().delete(request, *args, **kwargs)