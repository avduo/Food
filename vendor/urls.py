from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.productitems_category, name='productitems_category'),

    #CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    #Product CRUD
    path('menu-builder/product/add/', views.add_product, name='add_product'),
    path('menu-builder/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('menu-builder/product/delete/<int:pk>/', views.delete_product, name='delete_product'),

    #Opening Hours CRUD
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/delete/<int:pk>/', views.delete_opening_hours, name='delete_opening_hours'),
    # path('opening-hours/edit<int:pk>/', views.edit_opening_hours, name='edit_opening_hours'),
]