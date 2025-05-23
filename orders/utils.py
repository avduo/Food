import datetime
from django.conf import settings

from accounts.utils import send_notification_email
from vendor.models import Vendor
from .models import OrderedProduct



def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number

def send_customer_confirmation(order):
    mail_subject = 'Thank you for ordering with FoodOnline'
    mail_template = 'orders/order_confirmaton_email.html'
    to_email = {order.user.email, order.email}
    context = {
        'user': order.user,
        'order': order,
        'ordered_products': OrderedProduct.objects.filter(order=order),
        'to_email':  to_email,
    }
    send_notification_email(mail_subject, mail_template, context)


def send_vendor_notifications(order, cart_items):
    # Send order recieved email to the vendor
    mail_subject = 'Order received'
    mail_template = 'orders/order_received_email.html'
    # print([(i.product_item.product_title, i.product_item.vendor.vendor_name) for i in cart_items])

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