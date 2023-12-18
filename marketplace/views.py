from django.shortcuts import render, get_object_or_404
from .context_processors import get_cart_counter, get_cart_amounts
from django.http import HttpResponse, JsonResponse

from vendor.models import Vendor
from menu.models import Category, ProductItem
from django.db.models import Prefetch
from .models import Cart
from django.contrib.auth.decorators import login_required


def marketplace(request):
    vendors = Vendor.objects.filter(is_verified=True, user__is_active=True)
    vendor_count = vendors.count()
    # print(vendors)
    context = {
        'vendors' : vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'productitems',
            queryset = ProductItem.objects.filter(is_available=True)
        )
    )

    if  request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        # if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if product exists
            try:
                product_item = ProductItem.objects.get(id=product_id)
                #Check if user has already added product to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, product_item=product_item)
                    #Increase cart qty
                    chkCart.quantity +=1
                    chkCart.save()
                    return JsonResponse ({'status': 'Success', 'message': 'This product has been added to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, product_item=product_item, quantity=1)
                    return JsonResponse ({'status': 'Success', 'message': 'The cart has been created and this product has been added', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})

            except:
                return JsonResponse ({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse ({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse ({'status': 'login_required', 'message': 'Please login to continue'})

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        # if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if product exists
            try:
                product_item = ProductItem.objects.get(id=product_id)
                #Check if user has already removed product to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, product_item=product_item)
                    if chkCart.quantity > 1:
                    #Decrease cart qty
                        chkCart.quantity -=1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse ({'status': 'Success', 'message': 'This product has been removed from the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse ({'status': 'Failed', 'message': 'You do not have this product in your cart', 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})

            except:
                return JsonResponse ({'status': 'Failed', 'message': 'This product does not exist in your cart!'})
        else:
            return JsonResponse ({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse ({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url= 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items' : cart_items
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
       # if request.is_ajax():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse ({'status': 'Sucess', 'message': 'Product removed from your cart!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse ({'status': 'Failed', 'message': 'This product does not exist in your cart!'})
        else:
            return JsonResponse ({'status': 'Failed', 'message': 'Invalid request!'})