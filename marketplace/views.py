from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

from vendor.models import Vendor
from menu.models import Category, ProductItem
from django.db.models import Prefetch
from .models import Cart


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
                    return JsonResponse ({'status': 'Success', 'message': 'This product has been added to the cart'})
                except:
                    chkCart = Cart.objects.create(user=request.user, product_item=product_item, quantity=1)
                    return JsonResponse ({'status': 'Success', 'message': 'The cart has been created and this product has been added'})

            except:
                return JsonResponse ({'status': 'Failed', 'message': 'This product does not exist!'})
        else:
            return JsonResponse ({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse ({'status': 'Failed', 'message': 'Please login to continue'})