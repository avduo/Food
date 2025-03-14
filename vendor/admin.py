from django.contrib import admin
from vendor.models import Vendor, OpeningHours

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'is_verified', 'vendor_siret', 'created_at')
    list_display_links = ('user', 'vendor_name', 'vendor_siret')
    list_editable = ('is_verified',)

class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day', 'opening_time', 'closing_time')
    # list_display_links = ('vendor', 'day', 'start_time', 'end_time')
    # list_editable = ('day', 'start_time', 'end_time')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHours, OpeningHoursAdmin)