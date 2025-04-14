from django.db import models
from accounts.models import User
from menu.models import ProductItem

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('Razorpay', 'Razorpay'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
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
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    is_ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def name(self):
        return f'{self.first_name} {self.last_name}'

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