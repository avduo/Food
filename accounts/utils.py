from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'customerDashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl

def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    #mail_subject = 'Please activate your new account' or 'Account password reset'
    message = render_to_string(email_template,{ # 'accounts/emails/accounts_verification_email.html' or # 'accounts/emails/reset_password_email.html'
        'user' : user,
        'domain': str(current_site), #converts current site to string
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, to=[to_email] ) # Use 'to' instead of '[to_email]'
    mail.content_subtype = 'html'  # Set the content type to HTML if your template is HTML
    mail.send()

def send_notification_email(mail_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    #current_site = get_current_site(request)
    message = render_to_string(email_template, context, #{
       #  'domain': str(current_site),
       #  }
    )
    to_email = context['user'].email
    mail = EmailMessage(mail_subject, message, to=[to_email] )
    mail.content_subtype = 'html'  # Set the content type to HTML if your template is HTML
    mail.send()