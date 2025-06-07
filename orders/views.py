from datetime import datetime, timezone
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import simplejson as json
import uuid
from django.shortcuts import redirect, render

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import ProductItem
from orders.forms import OrderForm
from orders.models import Order, OrderedProduct, Payment
from vendor.models import Vendor
from .utils import generate_order_number, send_customer_confirmation, send_vendor_notifications
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
import logging
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.product_item.vendor.id not in vendors_ids:
            vendors_ids.append(i.product_item.vendor.id)

    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        productitem = ProductItem.objects.get(pk=i.product_item.id, vendor_id__in=vendors_ids)
        v_id = productitem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (productitem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (productitem.price * i.quantity)
            k[v_id] = subtotal


        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_ammount = float(round((tax_percentage * subtotal) / 100, 2))
            tax_dict.update({tax_type: {str(tax_percentage) : tax_ammount}})
        # Contruct total data
        total_data.update({productitem.vendor.id:{str(subtotal): str(tax_dict)}})

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
            order.payment_method = request.POST.get('payment-method', 'Stripe')
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
             }
            # Payment method specific settings
            if order.payment_method == 'PayPal':
                context['PayPal'] = True  # Triggers PayPal
            elif order.payment_method == 'Stripe':
                context.update({
                    'Stripe': True,  # Triggers Stripe
                    'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                })
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
        send_customer_confirmation(order)

        # # Send order recieved email to the vendor
        send_vendor_notifications(order, cart_items)

        response = {
            'order_number': order.order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)

    return HttpResponse ('Payment view')

def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id') or request.GET.get('session_id')

    # print("\n=== NEW REQUEST ===")  # Visual separator in logs
    # print(f"Incoming GET params: {request.GET}")

    if request.GET.get('payment_success') == 'stripe':
        session_id = request.GET.get('session_id')
        # print(f"Found Stripe callback with session_id: {session_id}")

        if session_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                # print(f"Full session data:\n{session}")
                # print(f"Payment status: {session.payment_status}")
                # print(f"Session metadata: {session.metadata}")

                if session.payment_status == 'paid':
                    order_number = session.metadata.get('order_number')
                    # print(f"Extracted order_number: {order_number}")

                    if order_number:
                        redirect_url=(f'/orders/order-complete/?order_no={order_number}&trans_id={session_id}')
                        # print(f"Attempting redirect to: {redirect_url}")
                        # cart_items.delete()

                        return redirect(redirect_url)
                    else:
                        print("ERROR: No order_number in metadata")
                else:
                    print(f"Payment not complete. Status: {session.payment_status}")

            except Exception as e:
                print(f"EXCEPTION: {str(e)}")

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)
        Cart.objects.filter(user=order.user).delete()

        subtotal = 0
        for item in ordered_products:
            subtotal += (item.price * item.quantity)

        Cart.objects.filter(user=order.user).delete()

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

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        try:
            # Find payment by either session ID (initial) or payment intent (final)
            payment = Payment.objects.get(
                transaction_id=f'{session.id}'
            )

            # Update to final transaction ID
            payment.status = 'Completed'
            payment.save()

            # SAFELY get order through reverse relation
            try:
                orders = Order.objects.filter(payment=payment)
                if orders.exists():
                    order = orders.first()
                    order.is_ordered = True
                    order.save()


                # Process ordered products
                cart_items = Cart.objects.filter(user=order.user)
                for item in cart_items:
                    OrderedProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=order.user,
                        product_item=item.product_item,
                        quantity=item.quantity,
                        price=item.product_item.price,
                        total_price=item.product_item.price * item.quantity
                    )

                send_customer_confirmation(order)
                send_vendor_notifications(order, cart_items)
                # logger.info(f'Webhook received for session: {session.id}')

            except Order.DoesNotExist:
                logger.error(f"[Webhook] No order found for payment {payment.id}")
                return HttpResponse(status=400)

        except Payment.DoesNotExist:
            logger.error(f"[Webhook] No payment found for session {session.id}")
            return HttpResponse(status=400)

        except Exception as e:
            logger.error(f"[Webhook] General failure: {str(e)}")
            return HttpResponse(status=400)

    return HttpResponse(status=200)

def handle_stripe_payment_success(session):
    order_number = session.metadata.get('order_number')
    payment_intent = session.payment_intent

    try:
        order = Order.objects.get(order_number=order_number)
        payment = Payment.objects.get(order=order)

        payment.transaction_id = payment_intent  # Update to final ID
        payment.status = 'Completed'
        payment.save()

        # order = payment.order
        order.is_ordered = True
        order.save()

        # Move cart items to ordered products (same as PayPal flow)
        cart_items = Cart.objects.filter(user=order.user)
        for item in cart_items:
            OrderedProduct.objects.create(
                order=order,
                payment=payment,
                user=order.user,
                product_item=item.product_item,
                quantity=item.quantity,
                price=item.product_item.price,
                total_price=item.product_item.price * item.quantity
            )

        # Send emails (same as PayPal flow)
        send_customer_confirmation(order)
        send_vendor_notifications(order, cart_items)

    except Order.DoesNotExist:
        # Handle missing order error
        logger.error(f"No order found for order_number {order_number}")
    except Payment.DoesNotExist:
        logger.error(f"No payment found for order {order.id}")
    except Exception as e:
        logger.error(f"Error handling Stripe payment success: {str(e)}")

@require_POST
@login_required
def create_stripe_checkout_session(request):
    try:
        data = json.loads(request.body)
        order = Order.objects.get(
            order_number=data.get('order_number'),
            is_ordered=False
        )

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(order.total * 100),
                    'product_data': {
                        'name': f'{order.first_name} {order.last_name}, your Order #{order.order_number}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url = request.build_absolute_uri('/orders/order-complete/') + '?payment_success=stripe&session_id={CHECKOUT_SESSION_ID}',
            # success_url = request.build_absolute_uri('/cart/?payment_success=stripe&session_id={CHECKOUT_SESSION_ID}'),
            # success_url=request.build_absolute_uri(
            #     f'/orders/order-complete/?'
            #     f'order_no={order.order_number}&'
            #     f'trans_id=STRIPE_{"{CHECKOUT_SESSION_ID}"}&'
            #     f'payment_method=stripe'
            # ),
            cancel_url=request.build_absolute_uri('/cart/?payment_canceled=true'),
            metadata={
                'order_number': order.order_number,
                'user_id': request.user.id

            }
        )
        # print("✅ Stripe Session Success URL:", session.success_url),


        payment = Payment.objects.create(
            user=request.user,
            transaction_id=f'{session.id}',  # Start with session ID
            payment_method='Stripe',
            amount=order.total,
            status='Pending',
            raw_response=json.dumps(session)
        )

        order.payment = payment
        order.save()

        return JsonResponse({
            'sessionId': session.id,
            'order_number': order.order_number,
            'transaction_id': payment.transaction_id,
            'checkout_url': session.url,
        })

    except Exception as e:
        logger.error(f"Stripe session error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)