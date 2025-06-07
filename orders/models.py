from decimal import Decimal
import json
from django.db import models

from accounts.models import User
from menu.models import ProductItem
from vendor.models import Vendor

request_object = ''
class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('Stripe', 'Stripe'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    raw_response = models.JSONField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id

class Order(models.Model):
    STATUS = (
        ('Paid', 'Paid'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,  null=True, blank=True)
    country = models.CharField(max_length=100, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percent':'tax_amount'}}")
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=20, choices=STATUS, default='Paid')
    is_ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def name(self):
        return f'{self.first_name} {self.last_name}'

    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        vendor = Vendor.objects.get(user=request_object.user)

        subtotal = 0
        tax = 0
        tax_dict = {}

        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))

            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'", '"')
                val = json.loads(val)
                tax_dict.update(val)

                # calculate tax
                #{'TVA': {'20.00': 9.2}, 'Purchase Protection': {'5.00': 2.3}}
                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])

        grand_total = float(subtotal) + float(tax)
        context = {
            'subtotal': subtotal,
            'tax': tax,
            'tax_dict': tax_dict,
            'grand_total': grand_total,
        }


        return context

    def __str__(self):
        return self.order_number

class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_item.product_title