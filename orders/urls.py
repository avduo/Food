from . import views
from django.urls import path

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order-complete/', views.order_complete, name='order_complete'),

]