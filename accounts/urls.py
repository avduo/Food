from django.urls import path
from . import views

urlpatterns = [
    path('register-user/', views.registerUser, name='registerUser'),
    path('register-vendor/', views.registerVendor, name='registerVendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my-account/', views.myAccount, name='myAccount'),
    path('customer-dashboard/', views.customerDashboard, name='customerDashboard'),
    path('vendor-dashboard/', views.vendorDashboard, name='vendorDashboard'),
]