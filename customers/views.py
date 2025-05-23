
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedProduct
import simplejson as json

# Create your views here.

@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context ={
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)

def cmyOrders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-ordered_at')
    context = {
        'orders': orders,
    }
    return render(request, 'customers/cmyorders.html', context)

def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'tax_data': tax_data,
        }
    except:
        return redirect('customer')
    return render(request, 'customers/order_detail.html', context)