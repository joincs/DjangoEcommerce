from django.contrib import admin
from .models import Product,Vairation,ProductImage, Category,ProductFeatured

# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class VairationInline(admin.TabularInline):
    model = Vairation
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__','price']
    inlines = [
        VairationInline,
        ProductImageInline
    ]
    class Meta:
        model = Product
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ProductFeatured)