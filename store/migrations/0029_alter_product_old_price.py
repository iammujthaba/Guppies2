# Generated by Django 5.0.6 on 2024-08-18 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_order_confirmed_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=7, null=True),
        ),
    ]
