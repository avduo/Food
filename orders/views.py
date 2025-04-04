from datetime import timezone
import simplejson as json
import uuid
from django.shortcuts import redirect, render

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order
from .utils import generate_order_number


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = request.user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.city = form.cleaned_data['city']
            order.state = form.cleaned_data['state']
            order.post_code = form.cleaned_data['post_code']
            order.country = form.cleaned_data['country']
            order.total_tax = total_tax
            order.total = grand_total
            order.payment_method = request.POST['payment-method']
            order.tax_data = json.dumps(tax_data)
            order.is_ordered = True
            # order.ordered_at = timezone.now()
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            # cart_items.delete()
            return redirect('place_order')
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')