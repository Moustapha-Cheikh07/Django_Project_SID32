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
from django.db.models import Avg, Max
from dateutil.relativedelta import relativedelta
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def home(request):
    # Statistiques de base
    total_products = Product.objects.count()
    total_points_of_sale = PointOfSale.objects.count()
    total_carts = Cart.objects.count()

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
            'month': date.strftime('%B %Y'),
            'inpc': round(valeur_inpc, 2)
        })

    # Prix moyens par point de vente pour chaque produit
    products = Product.objects.all()
    points_of_sale = PointOfSale.objects.all()
    
    # Récupérer le product_id de l'URL ou utiliser le premier produit par défaut
    default_product = products.first()
    selected_product_id = request.GET.get('product_id')
    
    # Si aucun produit n'est sélectionné et qu'il y a des produits, utiliser le premier
    if not selected_product_id and default_product:
        selected_product_id = str(default_product.id)
    
    print(f"Selected product ID: {selected_product_id}")  # Debug log
    
    # Initialiser les listes pour les données du graphique
    avg_prices_labels = []
    avg_prices_data = []
    
    if selected_product_id:
        # Calculer la moyenne des prix pour chaque point de vente
        from django.db.models import F
        from django.db.models.functions import ExtractMonth, ExtractYear
        
        # Obtenir la date actuelle
        current_date = datetime.now().date()
        print(f"Current date: {current_date}")  # Debug log
        
        # Récupérer tous les prix pour le produit sélectionné
        all_prices = ProductPrice.objects.filter(
            product_id=selected_product_id
        )
        print(f"Total prices found: {all_prices.count()}")  # Debug log
        
        # Filtrer les prix valides à la date actuelle
        avg_prices = all_prices.filter(
            date_from__lte=current_date,
            date_to__gte=current_date
        ).values(
            'point_of_sale',
            'point_of_sale__name'
        ).annotate(
            avg_price=Avg('value')
        ).order_by('point_of_sale__name')
        
        print(f"Prices after date filter: {avg_prices.count()}")  # Debug log
        print("Query:", avg_prices.query)  # Debug log
        
        # Si aucun prix n'est trouvé avec le filtre de date, prendre les prix les plus récents
        if not avg_prices.exists():
            print("No prices found with date filter, getting latest prices")  # Debug log
            latest_prices = all_prices.values(
                'point_of_sale'
            ).annotate(
                latest_date_from=Max('date_from')
            )
            
            avg_prices = all_prices.filter(
                date_from__in=[p['latest_date_from'] for p in latest_prices]
            ).values(
                'point_of_sale',
                'point_of_sale__name'
            ).annotate(
                avg_price=Avg('value')
            ).order_by('point_of_sale__name')
        
        # Créer un dictionnaire des prix moyens par point de vente
        price_dict = {
            price['point_of_sale']: price['avg_price']
            for price in avg_prices
        }
        
        print(f"Final price dictionary: {price_dict}")  # Debug log
        
        # Ajouter les données pour chaque point de vente
        for pos in points_of_sale:
            avg_prices_labels.append(pos.name)
            if pos.id in price_dict:
                avg_prices_data.append(float(price_dict[pos.id]))
            else:
                avg_prices_data.append(0)
        
        print(f"Final labels: {avg_prices_labels}")  # Debug log
        print(f"Final data: {avg_prices_data}")  # Debug log

    # Convertir selected_product_id en entier pour la comparaison dans le template
    selected_product_id = int(selected_product_id) if selected_product_id else None

    # Données pour les autres graphiques
    product_types = ProductType.objects.all()
    
    # Données pour le diagramme circulaire des types de produits
    product_type_labels = [pt.label for pt in product_types]
    product_type_data = [Product.objects.filter(product_type=pt).count() for pt in product_types]
    
    # Données pour l'évolution de l'INPC par produit
    inpc_by_product_data = []
    inpc_by_product_labels = []
    for product in products[:10]:  # Limiter aux 10 premiers produits pour la lisibilité
        prices = ProductPrice.objects.filter(product=product).order_by('date_from')
        if prices.exists():
            inpc_by_product_data.append([price.value for price in prices])
            inpc_by_product_labels.append(product.name)  # Utilisation de name au lieu de label
    
    # Données pour l'évolution de l'INPC Global
    global_inpc_data = []
    global_inpc_labels = []
    prices = ProductPrice.objects.order_by('date_from').values('date_from').distinct()
    for price_date in prices:
        date = price_date['date_from']
        avg_price = ProductPrice.objects.filter(date_from=date).aggregate(Avg('value'))['value__avg']
        if avg_price:
            global_inpc_data.append(float(avg_price))
            global_inpc_labels.append(date.strftime('%Y-%m-%d'))

    context = {
        'total_products': total_products,
        'total_points_of_sale': total_points_of_sale,
        'total_carts': total_carts,
        'inpc_last_4_months': inpc_last_4_months,
        'product_type_labels': product_type_labels,
        'product_type_data': product_type_data,
        'inpc_by_product_labels': inpc_by_product_labels,
        'inpc_by_product_data': inpc_by_product_data,
        'global_inpc_labels': global_inpc_labels,
        'global_inpc_data': global_inpc_data,
        'products': products,
        'selected_product_id': selected_product_id,
        'avg_prices_labels': avg_prices_labels,
        'avg_prices_data': avg_prices_data,
    }
    return render(request, 'inpc/home.html', context)


def calculate_inpc_for_date(date):
    """
    Fonction utilitaire pour calculer l'INPC pour une date donnée.
    """
    logger.debug(f"Calculating INPC for date: {date.strftime('%Y-%m-%d')}")
    
    # Calculer le prix moyen de chaque produit pour la période donnée
    product_avg_prices = {}
    month_start = date.replace(day=1)
    month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
    
    logger.debug(f"Period: {month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')}")
    
    # Log le nombre total de produits
    total_products = Product.objects.count()
    logger.debug(f"Total number of products: {total_products}")
    
    # Récupérer tous les prix valides pour la période
    valid_prices = ProductPrice.objects.filter(
        date_from__lte=month_end,
        date_to__isnull=True
    ) | ProductPrice.objects.filter(
        date_from__lte=month_end,
        date_to__gte=month_start
    )
    
    logger.debug(f"Total valid prices found: {valid_prices.count()}")
    
    # Calculer le prix moyen par produit
    for product in Product.objects.all():
        product_prices = valid_prices.filter(product=product)
        avg_price = product_prices.aggregate(Avg('value'))['value__avg']
        
        logger.debug(f"Product {product.id} ({product.name}): Found {product_prices.count()} prices, Average = {avg_price}")
        
        if avg_price is not None:
            product_avg_prices[product.id] = avg_price

    if not product_avg_prices:
        logger.warning(f"No average prices found for {date.strftime('%Y-%m')}, returning 0.")
        return 0

    logger.debug(f"Number of products with valid prices: {len(product_avg_prices)}")

    # Récupérer tous les produits de panier valides pour la période
    valid_cart_products = CartProduct.objects.filter(
        date_from__lte=month_end,
        date_to__isnull=True
    ) | CartProduct.objects.filter(
        date_from__lte=month_end,
        date_to__gte=month_start
    )
    
    logger.debug(f"Total valid cart products found: {valid_cart_products.count()}")

    # Calculate INPC for each cart
    cart_inpc = {}
    total_carts = Cart.objects.count()
    logger.debug(f"Total number of carts: {total_carts}")
    
    for cart in Cart.objects.all():
        cart_products = valid_cart_products.filter(cart=cart)
        logger.debug(f"Cart {cart.id} ({cart.name}): Found {cart_products.count()} valid products")
        
        total_weighted_price = 0
        total_weight = 0

        for cart_product in cart_products:
            product_id = cart_product.product.id
            if product_id in product_avg_prices:
                price = product_avg_prices[product_id]
                weight = cart_product.weight
                total_weighted_price += price * weight
                total_weight += weight
                logger.debug(f"Cart {cart.id}, Product {product_id}: Price={price}, Weight={weight}")

        if total_weight > 0:
            cart_inpc[cart.id] = total_weighted_price / total_weight
            logger.debug(f"Cart {cart.id}: INPC = {cart_inpc[cart.id]} (total_weight={total_weight})")
        else:
            logger.warning(f"Cart {cart.id}: Total weight is 0 - Check if cart products exist and are valid for {date.strftime('%Y-%m')}")
            cart_inpc[cart.id] = 0

    if not cart_inpc:
        logger.warning(f"No cart INPC found for {date.strftime('%Y-%m')}, returning 0.")
        return 0

    logger.debug(f"Number of carts with valid INPC: {len(cart_inpc)}")

    # Calculate global INPC
    global_inpc = sum(cart_inpc.values()) / len(cart_inpc)
    logger.debug(f"Final Global INPC: {global_inpc}")
    
    return global_inpc


@login_required
def calculate_inpc(request):
    """
    Vue Django pour calculer l'INPC en fonction des données soumises par l'utilisateur.
    Utilise 2019 comme année de base selon la méthodologie de l'INPC en Mauritanie.
    """
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            date = datetime(year, month, 1)  # Créer un objet datetime pour le début du mois

            # Année de base (2019) selon la méthodologie de l'INPC en Mauritanie
            base_year = 2019
            base_month = 1  # Janvier comme mois de base
            base_date = datetime(base_year, base_month, 1)

            # Calculer l'INPC global pour l'année de base (2019)
            base_inpc = calculate_inpc_for_date(base_date)
            
            # Log pour le débogage
            logger.debug(f"Base INPC (2019-01): {base_inpc}")

            # Calculer l'INPC global pour la période donnée
            current_inpc = calculate_inpc_for_date(date)
            
            # Log pour le débogage
            logger.debug(f"Current INPC ({date.strftime('%Y-%m')}): {current_inpc}")

            # Normaliser l'INPC global par rapport à l'année de base
            if base_inpc > 0:
                inpc_global = (current_inpc / base_inpc) * 100  # Base 100 = 2019
                logger.debug(f"Calculated Global INPC: {inpc_global}")
            else:
                logger.warning("Base INPC is 0 for 2019-01. Please ensure there is price data for January 2019")
                inpc_global = 0

            # Préparer le contexte pour le template
            context = {
                'inpc': round(inpc_global, 2),  # Arrondir à 2 décimales
                'month': month,
                'year': year,
                'base_year': base_year
            }
            return render(request, 'inpc/inpc_result.html', context)

        except ValueError as e:
            messages.error(request, f"Erreur de format : Veuillez vérifier le mois et l'année saisis. {str(e)}")
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'INPC: {str(e)}")
            messages.error(request, f"Erreur lors du calcul de l'INPC : {str(e)}")
    
    return render(request, 'inpc/inpc_form.html')

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
    queryset = model.objects.all()
    
    # Préparer les données pour l'exportation
    data = []
    for obj in queryset:
        item = {}
        for field in obj._meta.fields:
            if field.is_relation:
                item[field.name] = getattr(obj, field.name).code  # Utiliser le code de la clé étrangère
            else:
                item[field.name] = getattr(obj, field.name)
        data.append(item)
    
    # Créer un DataFrame à partir des données
    df = pd.DataFrame(data)
    
    # Créer un buffer en mémoire pour le fichier Excel
    output = io.BytesIO()
    
    # Utiliser pandas.ExcelWriter pour écrire le DataFrame dans le buffer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # Replacer le pointeur au début du buffer
    output.seek(0)
    
    # Créer l'objet HttpResponse avec le fichier Excel
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
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
    
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, ProductPrice
from django.db.models import Avg
from datetime import datetime

# ... vos autres vues existantes ...

@login_required
def price_evolution(request):
    """Vue pour afficher la page d'évolution des prix"""
    products = Product.objects.all().order_by('name')
    context = {
        'products': products,
        'selected_product': request.GET.get('product'),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
    }
    return render(request, 'inpc/price_evolution.html', context)

@login_required
def price_evolution_data(request):
    """Vue API pour récupérer les données du graphique"""
    try:
        product_id = request.GET.get('product')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([product_id, start_date, end_date]):
            return JsonResponse({'error': 'Paramètres manquants'}, status=400)

        # Récupérer les prix pour le produit et la période donnée
        prices = ProductPrice.objects.filter(
            product_id=product_id,
            date_from__gte=start_date,
            date_from__lte=end_date
        ).values('date_from').annotate(
            avg_price=Avg('value')
        ).order_by('date_from')

        # Formater les données pour le graphique
        data = {
            'labels': [price['date_from'].strftime('%Y-%m-%d') for price in prices],
            'values': [float(price['avg_price']) for price in prices]
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from chartjs.views.lines import BaseLineChartView
from chartjs.views.columns import BaseColumnsHighChartsView
from .models import Product, ProductPrice, PointOfSale, ProductType

@login_required
def product_inpc_line_chart(request):
    """Vue pour afficher le graphique de l'INPC par produit"""
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'inpc/product_inpc_line_chart.html', context)

class ProductTypePieChart(BaseLineChartView):
    def get_labels(self):
        # Retourner les labels des types de produits
        return [pt.label for pt in ProductType.objects.all()]

    def get_data(self):
        # Calculer le nombre de produits pour chaque type
        data = []
        for product_type in ProductType.objects.all():
            count = Product.objects.filter(product_type=product_type).count()
            data.append(count)
        return [data]


class AvgProductPriceByPOSChart(BaseColumnsHighChartsView):
    def get_labels(self):
        return [pos.name for pos in PointOfSale.objects.all()]

    def get_data(self):
        data = []
        for pos in PointOfSale.objects.all():
            avg_price = ProductPrice.objects.filter(point_of_sale=pos).aggregate(Avg('value'))['value__avg']
            data.append(avg_price if avg_price is not None else 0)
        return [data]


class ProductINPCLineChart(BaseLineChartView):
    def get_labels(self):
        dates = []
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        date = start_date
        while date <= end_date:
            dates.append(date.strftime('%Y-%m-%d'))
            date += timedelta(days=1)
        return dates

    def get_providers(self):
        return ["INPC"]

    def get_data(self):
        product_id = self.request.GET.get('product')
        if not product_id:
            return [[0 for _ in self.get_labels()]]

        product = Product.objects.get(id=product_id)
        dates = self.get_labels()
        inpc_values = []

        for date_str in dates:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            avg_price = ProductPrice.objects.filter(
                product=product,
                date_from__lte=date,
                date_to__gte=date
            ).aggregate(Avg('value'))['value__avg']

            if avg_price is None:
                inpc_values.append(None)
            else:
                inpc_values.append(float(avg_price))

        return [inpc_values]


class GlobalINPCLineChart(BaseLineChartView):
    def get_labels(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if not start_date or not end_date:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        dates = []
        date = start_date
        while date <= end_date:
            dates.append(date.strftime('%Y-%m-%d'))
            date += timedelta(days=1)
        return dates

    def get_providers(self):
        return ["INPC Global"]

    def get_data(self):
        dates = self.get_labels()
        inpc_values = []

        for date_str in dates:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            avg_price = ProductPrice.objects.filter(
                date_from__lte=date,
                date_to__gte=date
            ).aggregate(Avg('value'))['value__avg']

            if avg_price is None:
                inpc_values.append(None)
            else:
                inpc_values.append(float(avg_price))

        return [inpc_values]


# Ensure these are properly defined

avg_product_price_by_pos_chart = AvgProductPriceByPOSChart.as_view()
product_inpc_line_chart_view = ProductINPCLineChart.as_view()
global_inpc_line_chart_view = GlobalINPCLineChart.as_view()
