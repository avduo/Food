import datetime
# import json
import simplejson as json
from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from accounts.utils import send_notification_email
from vendor.models import Vendor
from .models import OrderedProduct


def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number

current_site = Site.objects.get_current()
def send_customer_confirmation(order):
    mail_subject = 'Thank you for ordering with FoodOnline'
    mail_template = 'orders/order_confirmaton_email.html'
    ordered_products = OrderedProduct.objects.filter(order=order)
    c_subtotal = 0
    for item in ordered_products:
        c_subtotal += item.price * item.quantity
    tax_data = json.loads(order.tax_data)
    to_email = {order.user.email, order.email}

    context = {
        'user': order.user,
        'order': order,
        'ordered_products': ordered_products,
        'c_subtotal': c_subtotal,
        'tax_data': tax_data,
        'to_email':  to_email,
        'domain': current_site.domain,
    }
    send_notification_email(mail_subject, mail_template, context)


def send_vendor_notifications(order, cart_items):
    # Send order recieved email to the vendor
    mail_subject = 'Order received'
    mail_template = 'orders/order_received_email.html'

    # Collect unique vendor emails
    to_emails = []

    for i in cart_items:
        if i.product_item.vendor.user.email not in to_emails:
            to_emails.append(i.product_item.vendor.user.email)

            ordered_products = OrderedProduct.objects.filter(
                order=order,
                product_item__vendor=i.product_item.vendor)

            context = {
                'order': order,
                'to_email': i.product_item.vendor.user.email,
                'vendor_name': i.product_item.vendor.vendor_name,
                'ordered_products': ordered_products,
                'v_subtotal': order_total_by_vendor(order, i.product_item.vendor.id)['subtotal'],
                'tax_data': order_total_by_vendor(order, i.product_item.vendor_id)['tax_dict'],
                'grand_total': order_total_by_vendor(order, i.product_item.vendor_id)['grand_total'],
                'domain': current_site.domain,
            }

            send_notification_email(mail_subject, mail_template, context)

def order_total_by_vendor(order, vendor_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = 0
    tax = 0
    tax_dict = {}

    for key, val in data.items():
        subtotal += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)

        filtered_val = {}
        for tax_name, tax_info in val.items():
            if tax_name != "Purchase Protection":
                filtered_val[tax_name] = tax_info
        tax_dict.update(filtered_val)

        # calculate tax
        #{'TVA': {'20.00': 9.2}, 'Purchase Protection': {'5.00': 2.3}}
        for i in filtered_val:
            for j in filtered_val[i]:
                tax += float(filtered_val[i][j])

    grand_total = float(subtotal) + float(tax)
    context = {
        'subtotal': subtotal,
        'tax': tax,
        'tax_dict': tax_dict,
        'grand_total': grand_total,
    }


    return context