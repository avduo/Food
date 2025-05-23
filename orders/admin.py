from django.contrib import admin
from .models import Payment, Order, OrderedProduct

class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ['payment', 'user', 'product_item', 'quantity', 'price', 'total_price']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderedProductInline]
    list_display = ['order_number', 'is_ordered', 'payment_method', 'first_name', 'last_name', 'phone', 'email', 'post_code', 'total', 'total_tax', 'status', 'ordered_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email', 'post_code', 'country']
    date_hierarchy = 'ordered_at'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'status', 'payment_method', 'amount', 'created_at', 'updated_at']

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderedProduct)
