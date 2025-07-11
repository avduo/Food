import datetime
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from orders.models import Order
from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from  django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.template.defaultfilters import slugify

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied
        messages.danger(request, 'You are not autherised to view this page!')


# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        #print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            #password = form.cleaned_data['password']
            #user = form.save(commit=False)
            #user.set_password(password)
            #user.role = User.CUSTOMER
            #form.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            passsword = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=passsword)
            user.role = user.CUSTOMER
            user.save()
            # Send verification Email
            mail_subject = 'Please activate your new account'
            email_template = 'accounts/emails/accounts_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            #print('User is created from create_user')
            messages.success(request, 'Your account has been created sucessfuly!')
            return redirect('registerUser')
        else:
            print(form.errors)  # Print form errors for debugging

    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        # store the data and create vendor
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            # Creating the Vendor user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            # Send verification Email
            mail_subject = 'Please activate your new vendor account'
            email_template = 'accounts/emails/accounts_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            # print('Restaurant is created from create_vendor')
            messages.success(request, 'Your Restaurant account has been created and will be approved in 48hrs ')
            return redirect('registerVendor')
        else:
            print('Invalid form')
            print(form.errors)

    form = UserForm()
    v_form = VendorForm()

    context = {
        'form':form,
        'v_form':v_form
    }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations your account has now been activated!')
        return redirect('myAccount')
    else:
        messages.error(request, 'Sorry your activation link is invalid!')
        return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Welcome you are now logged in to FoodOnline')
            return redirect('myAccount')
        else:
            messages.error(request,'Unable to find User and/or Password')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You have now been logged out, thank you for your visit.')
    return redirect('home')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-ordered_at')
    recent_orders = orders[:5]
    context = {
        'orders' : orders,
        'orders_count' : orders.count(),
        'recent_orders' : recent_orders,
    }
    return render(request, 'accounts/customerDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-ordered_at')
    recent_orders = orders[:10]

    # Current months revenue
    current_month = datetime.datetime.now().month
    current_months_orders = orders.filter(vendors__in=[vendor.id], ordered_at__month=current_month).order_by('-ordered_at')
    current_months_revenue = 0
    for i in current_months_orders:
        current_months_revenue += i.get_total_by_vendor()['grand_total']

    # Total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']

    context = {
        'orders' : orders,
        'orders_count' : orders.count(),
        'recent_orders' : recent_orders,
        'total_revenue' : total_revenue,
        'current_months_revenue' : current_months_revenue,
    }
    return render(request, 'accounts/vendorDashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            #Send reset email
            mail_subject = 'Account password reset'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your password reset link has been set to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Sorry this email address does not exist!')
            return redirect('login')

    return render(request, 'accounts/forgotPassword.html')

def resetPasswordValidate(request, uidb64, token):
    #Validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Sorry this link has expired or is invalid!')
        return redirect('myAccount')

def resetPassword(request):
    # if not request.user.is_superuser:
    #     return redirect('home')
    if 'uid' not in request.session:
        messages.error(request, 'Unauthorized access to password reset page.')
        return redirect('login')

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            try:
                pk = request.session.get('uid')
                user = User.objects.get (pk=pk)
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, 'You have reset your password, you can now sign in and have access to your account.')
                return redirect ('myAccount')
                pass
            except:
                messages.error(request, 'An error occurred while resetting your password.')
                return redirect('myAccount')
        else:
            messages.error(request, 'The passwords you have entered do not match!')
            return redirect('resetPassword')

    return render(request, 'accounts/resetPassword.html')