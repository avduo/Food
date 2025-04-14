from datetime import datetime, timezone
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import simplejson as json
import uuid
from django.shortcuts import redirect, render

from accounts.utils import send_notification_email
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order, OrderedProduct, Payment
from vendor.models import Vendor
from .utils import generate_order_number
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
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
            order.subtotal = subtotal
            order.total_tax = total_tax
            order.total = grand_total
            order.payment_method = request.POST['payment-method']
            order.tax_data = json.dumps(tax_data)
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            context = {
                 'order': order,
                 'cart_items': cart_items,
             }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    # Check if request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
    # Store payment details in the payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status,
        )
        payment.save()
        # Update order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cartitems to oredered product model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_product = OrderedProduct()
            ordered_product.order = order
            ordered_product.payment = payment
            ordered_product.user = request.user
            ordered_product.product_item = item.product_item
            ordered_product.quantity = item.quantity
            ordered_product.price = item.product_item.price
            ordered_product.total_price = item.product_item.price * item.quantity # Calculate the total amount of the order
            ordered_product.save()

        # Send order confirmed email to the customer
        mail_subject = 'Thank you for ordering with FoodOnline'
        mail_template = 'orders/order_confirmaton_email.html'
        to_email = {request.user.email, order.email}
        context = {
            'user': request.user,
            'order': order,
            'ordered_products': OrderedProduct.objects.filter(order=order),
            'to_email':  to_email,
        }
        send_notification_email(mail_subject, mail_template, context)

        # Send order recieved email to the vendor
        mail_subject = 'Order received'
        mail_template = 'orders/order_recieved_email.html'
        print([(i.product_item.product_title, i.product_item.vendor.vendor_name) for i in cart_items])

        # Collect unique vendor emails
        to_emails = []
        for i in cart_items:
            vendor_email = i.product_item.vendor.user.email
            if vendor_email not in to_emails:
                to_emails.append(vendor_email)
            #print(to_emails)
            #print(f"\nSTARTING PROCESSING FOR: {vendor_email}")

        # Process each vendor separately
        for vendor_email in to_emails:
            try:
                vendor = Vendor.objects.get(user__email=vendor_email)
                #print(f"Correctly retrieved: {vendor.vendor_name} for {vendor_email}")
            except Vendor.DoesNotExist:
                #print(f"ERROR: No vendor found for {vendor_email}")
                continue


            # Get only this vendor's items
            vendor_products = OrderedProduct.objects.filter(
                order=order,
                product_item__vendor__user__email=vendor_email
            )
            #print(f"Found {vendor_products.count()} products for this vendor")

            context = {
                'order': order,
                'ordered_products': vendor_products,
                'user': vendor.user,
                'vendor': vendor,
                'to_email': [vendor_email],
            }

            #Debug print before sending
            #print(f"FINISHED PROCESSING FOR: {vendor_email}")
            send_notification_email(mail_subject, mail_template, context)

        response = {
            'order_number': order.order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)

    return HttpResponse ('Payment view')

def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)

        subtotal = 0
        for item in ordered_products:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('cart')