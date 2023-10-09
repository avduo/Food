from django.core.exceptions import ValidationError
import os

def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]
    print(ext)
    valid_extensions = ['.png', '.jpeg', '.jpg', '.webp']
    if not ext.lower() in valid_extensions:
        raise ValidationError("Sorry you've tried to upload an unsupported file type! You can upload: " +str(valid_extensions))