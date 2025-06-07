from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.http import JsonResponse

from orders.models import Order, OrderedProduct
from .forms import VendorForm, OpeningHoursForm
from accounts.forms import UserProfileForm

from menu.forms import CategoryForm, ProductItemForm
from accounts.models import UserProfile
from .models import Vendor, OpeningHours
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, ProductItem
from django.template.defaultfilters import slugify

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Your restaurant details have been updated. ')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
            messages.error(request, 'Sorry your restaurant details have not beeen saved! ')
    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance = vendor)

    context = {
        'profile_form' : profile_form,
        'vendor_form' : vendor_form,
        'profile' : profile,
        'vendor' : vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories' : categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def productitems_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    productitems = ProductItem.objects.filter(vendor=vendor, category=category)
    context = {
        'productitems' : productitems,
        'category' : category,
    }
    print(productitems)
    return render(request, 'vendor/productitems_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request, 'New category has been saved successfuly! ')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form' : form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Your category has been updated successfuly! ')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form' : form,
        'category': category
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Your category has been deleted successfuly! ')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_product(request):
    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES)
        if form.is_valid():
            product_title = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(product_title)
            form.save()
            messages.success(request, 'Your product has been updated successfuly! ')
            return redirect('productitems_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = ProductItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form' : form,
    }
    return render(request, 'vendor/add_product.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_product(request, pk=None):
    product = get_object_or_404(ProductItem, pk=pk)
    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product_title = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(product_title)
            form.save()
            messages.success(request, 'Your product has been updated successfuly! ')
            return redirect('productitems_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = ProductItemForm(instance=product)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form' : form,
        'product': product
    }
    return render(request, 'vendor/edit_product.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_product(request, pk=None):
    product = get_object_or_404(ProductItem, pk=pk)
    product.delete()
    messages.success(request, 'Your product has been deleted successfuly! ')
    return redirect('productitems_category', product.category.id)

def opening_hours(request):
    opening_hours = OpeningHours.objects.filter(vendor=get_vendor(request))
    form = OpeningHoursForm()
    context = {
        'form' : form,
        'opening_hours' : opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    #Handle the data and save in the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            vendor = get_vendor(request)
            day = request.POST.get('day')
            opening_time = request.POST.get('opening_time')
            closing_time = request.POST.get('closing_time')
            is_closed = request.POST.get('is_closed') == 'true'

            try:
                hour = OpeningHours.objects.create(vendor=get_vendor(request), day=day, opening_time=opening_time, closing_time=closing_time, is_closed=is_closed)
                if hour:
                    day = OpeningHours.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'opening_time': hour.opening_time, 'closing_time': hour.closing_time}
                return JsonResponse(response)
            except IntegrityError as e:
                response ={'status': 'failed', 'message': 'Do opening times already exist?'}
                return JsonResponse(response)
        else:
            return HttpResponse('Invalid request')
    else:
        return HttpResponse('You are not authorized to add opening hours')

def delete_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHours, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})

def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order, product_item__vendor=get_vendor(request))
    except:
        return redirect('vendor')
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'subtotal': order.get_total_by_vendor()['subtotal'],
        'tax': order.get_total_by_vendor()['tax'],
        'grand_total': order.get_total_by_vendor()['grand_total'],
        'tax_data': order.get_total_by_vendor()['tax_dict'],
    }
    return render(request, 'vendor/order_detail.html', context)

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-ordered_at')
    context = {
        'orders' : orders,
    }
    return render(request, 'vendor/my_orders.html', context)