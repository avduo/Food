from django.db import models
from django.http import HttpRequest
from accounts.models import User, UserProfile
from accounts.utils import send_notification_email
from datetime import time, date, timedelta, datetime

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

    def is_open(self):
        # Check current day's opening hours
        today_date = date.today()
        today = today_date.isoweekday()

        current_opening_hours = OpeningHours.objects.filter(vendor=self, day=today)
        now = datetime.now().strftime("%I:%M %p")  # Convert current time to string (e.g., "07:00 PM")

        is_open = None
        for i in current_opening_hours:
            # Extract opening and closing times as strings
            opening_time = i.opening_time  # Already in "%I:%M %p" format (e.g., "07:00 PM")
            closing_time = i.closing_time  # Already in "%I:%M %p" format (e.g., "01:00 AM")

            # Handle the case where the shop is open past midnight
            if closing_time < opening_time:
                # Shop is open past midnight (e.g., Tuesday 7 PM to 1 AM)
                if now >= opening_time or now < closing_time:
                    is_open = True
                    break
            else:
                # Normal case (e.g., Tuesday 9 AM to 5 PM)
                if opening_time <= now < closing_time:
                    is_open = True
                    break

            # If neither condition is met, the shop is closed
            is_open = False

        return is_open

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

DAYS = [
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),
]

HOUR_OF_DAY = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24 ) for m in(0, 30)]
# HOUR_OF_DAY = [(lambda t: (t.strftime('%I:%M %p'), t.strftime('%I:%M %p')))((datetime.combine(datetime.today(), time(0, 30)) + timedelta(minutes=30 * i)).time()) for i in range(48)]

class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    opening_time = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    closing_time = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-opening_time')
        unique_together = ('vendor','day', 'opening_time', 'closing_time')

    def __str__(self):
        return self.get_day_display()
