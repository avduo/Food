from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order-complete/', views.order_complete, name='order_complete'),
    # Stripe payment routes
    path('create-stripe-session/', views.create_stripe_checkout_session, name='create-stripe-session'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),

]