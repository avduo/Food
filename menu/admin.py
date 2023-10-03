from django.contrib import admin
from .models import Category, ProductItem

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name')

class ProductItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_title',)}
    list_display = ('product_title', 'category', 'vendor', 'price', 'sale_price', 'is_avaliable', 'updated_at')
    search_fields = ('product_title', 'category__category_name', 'vendor__vendor_name', 'price')
    list_filter =('is_avaliable',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductItem, ProductItemAdmin)