# Generated by Django 4.2.5 on 2023-10-18 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_rename_is_avaliable_productitem_is_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productitems', to='menu.category'),
        ),
    ]