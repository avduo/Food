# Generated by Django 4.2.5 on 2023-10-18 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='productitem',
            new_name='product_item',
        ),
    ]
