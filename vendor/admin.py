from django.contrib import admin
from vendor.models import Vendor

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'is_verified', 'vendor_siret', 'created_at')
    list_display_links = ('user', 'vendor_name', 'vendor_siret')
    list_editable = ('is_verified',)
admin.site.register(Vendor, VendorAdmin)