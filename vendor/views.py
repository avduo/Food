from django.shortcuts import get_object_or_404, render, redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm

from menu.forms import CategoryForm, ProductItemForm
from accounts.models import UserProfile
from .models import Vendor
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