from django.urls import path
from .import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    #Add to cart
    path('add-to-cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    #Remove form cart
    path('remove-from-cart/<int:product_id>', views.remove_from_cart, name='remove_from_cart'),
    #Delete cart
    path('delete-cart/<int:cart_id>', views.delete_cart, name='delete_cart'),
]