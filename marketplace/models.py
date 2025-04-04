from django.db import models

from accounts.models import User
from menu.models import ProductItem

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user

class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'taxes'

    def __str__(self):
        return self.tax_type