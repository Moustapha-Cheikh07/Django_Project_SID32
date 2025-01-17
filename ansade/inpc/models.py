from django.db import models

class ProductType(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code du Type")
    label = models.CharField(max_length=100, verbose_name="Libellé du Type")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Type de Produit"
        verbose_name_plural = "Types de Produits"


class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code du Produit")
    name = models.CharField(max_length=100, verbose_name="Nom du Produit")
    description = models.TextField(blank=True, verbose_name="Description")
    unit_measure = models.CharField(max_length=50, verbose_name="Unité de Mesure")
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name="Type de Produit")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"


class Wilaya(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code de la Wilaya")
    name = models.CharField(max_length=100, verbose_name="Nom de la Wilaya")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Wilaya"
        verbose_name_plural = "Wilayas"


class Moughata(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code de la Moughata")
    label = models.CharField(max_length=100, verbose_name="Libellé de la Moughata")
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, verbose_name="Wilaya")

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Moughata"
        verbose_name_plural = "Moughatas"


class Commune(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code de la Commune")
    name = models.CharField(max_length=100, verbose_name="Nom de la Commune")
    moughata = models.ForeignKey(Moughata, on_delete=models.CASCADE, verbose_name="Moughata")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"


class PointOfSale(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code du Point de Vente")
    name = models.CharField(max_length=100, verbose_name="Nom du Point de Vente")
    gps_lat = models.FloatField(verbose_name="Latitude GPS")
    gps_lon = models.FloatField(verbose_name="Longitude GPS")
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, verbose_name="Commune")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Point de Vente"
        verbose_name_plural = "Points de Vente"


class Cart(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code du Panier")
    name = models.CharField(max_length=100, verbose_name="Nom du Panier")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="Panier")
    weight = models.FloatField(verbose_name="Pondération")
    date_from = models.DateField(verbose_name="Date de Début")
    date_to = models.DateField(null=True, blank=True, verbose_name="Date de Fin")

    def __str__(self):
        return f"{self.cart.name} - {self.product.name}"

    class Meta:
        verbose_name = "Produit dans le Panier"
        verbose_name_plural = "Produits dans les Paniers"


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    point_of_sale = models.ForeignKey(PointOfSale, on_delete=models.CASCADE, verbose_name="Point de Vente")
    value = models.FloatField(verbose_name="Valeur du Prix")
    date_from = models.DateField(verbose_name="Date de Début")
    date_to = models.DateField(null=True, blank=True, verbose_name="Date de Fin")

    def __str__(self):
        return f"{self.product.name} - {self.point_of_sale.name}"

    class Meta:
        verbose_name = "Prix du Produit"
        verbose_name_plural = "Prix des Produits"