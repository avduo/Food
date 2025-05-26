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
        # “now” as a datetime
        now = datetime.now()

        # Figure out today and yesterday as ISO weekdays
        today = now.isoweekday()                    # 1 = Monday … 7 = Sunday
        yesterday = 7 if today == 1 else today - 1

        # Fetch all records for today and yesterday
        today_blocks = OpeningHours.objects.filter(vendor=self, day=today)
        yesterday_blocks = OpeningHours.objects.filter(vendor=self, day=yesterday)

        # If *any* of today’s blocks is explicitly “closed all day”, we’re closed.
        if today_blocks.filter(is_closed=True).exists():
            return False

        # Helper to parse your "07:00 PM" strings
        def parse_time(t_str):
            return datetime.strptime(t_str, "%I:%M %p").time()

        # Check today’s blocks (including those that spill past midnight)
        for block in today_blocks:
            open_t = (block.opening_time or "").strip()
            close_t =(block.closing_time or "").strip()


            # SKIP any blank/malformed slots
            if not open_t or not close_t:
                continue

            # Build datetimes on today’s date
            open_dt  = datetime.combine(now.date(), parse_time(open_t))
            close_dt = datetime.combine(now.date(), parse_time(close_t))

            # If it really closes next day, add 1 day
            if close_dt <= open_dt:
                close_dt += timedelta(days=1)

            if open_dt <= now < close_dt:
                return True

        # Check yesterday’s overnight-only blocks
        for block in yesterday_blocks:
            open_t = parse_time(block.opening_time)
            close_t = parse_time(block.closing_time)

            # Only treat as overnight if close ≤ open
            if close_t <= open_t:
                open_dt  = datetime.combine(now.date() - timedelta(days=1), open_t)
                close_dt = datetime.combine(now.date(), close_t)

                if open_dt <= now < close_dt:
                    return True

        # If we never returned True, we’re closed
        return False

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
                        'to_email' : self.user.email,

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
        verbose_name_plural = 'Opening Hours'

    def __str__(self):
        return self.get_day_display()
