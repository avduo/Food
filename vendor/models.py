from django.db import models
from django.http import HttpRequest
from accounts.models import User, UserProfile
from accounts.utils import send_notification_email

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=250)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_siret = models.ImageField(upload_to='vendor/documents')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_verified != self.is_verified:
                mail_template = 'accounts/emails/vendor_approval_email.html'
                context = {
                        'user' : self.user,
                        'is_verified' : self.is_verified,
                        'vendor_name': self.vendor_name,

                    }
                if self.is_verified == True:
                    # Send Email Notification
                    mail_subject = "Congratulations, your restaurant has been approved on FoodOnline"
                    #mail_template = 'accounts/emails/vendor_approval_email.html'

                    send_notification_email(mail_subject, mail_template, context)
                else:
                    # Send Email Notification
                    mail_subject= "We're sorry, You are not able to create a reastuarant on FoodOnline"
                    #mail_template='accounts/emails/vendor__email.html'
                    send_notification_email(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)