from django.contrib import admin

from marketplace.models import Cart, Tax

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_item', 'quantity', 'updated_at')

class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')
    list_filter = ('is_active',)

admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)