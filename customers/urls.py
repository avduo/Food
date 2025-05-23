from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.customerDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my-orders/', views.cmyOrders, name='cmyorders'),
    path('order-detail/<int:order_number>/', views.order_detail, name='order_detail'),
]