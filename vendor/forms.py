from django import forms
from .models import Vendor, OpeningHours
from accounts.validators import allow_only_images_validator

class VendorForm(forms.ModelForm):
    vendor_siret = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ('vendor_name', 'vendor_siret')

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ('vendor', 'day', 'opening_time', 'closing_time', 'is_closed')