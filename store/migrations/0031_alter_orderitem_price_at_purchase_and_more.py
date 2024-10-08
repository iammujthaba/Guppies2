# Generated by Django 5.0.6 on 2024-08-19 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0030_alter_product_old_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price_at_purchase',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='new_price',
            field=models.DecimalField(decimal_places=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='purchasehistory',
            name='price_at_purchase',
            field=models.DecimalField(decimal_places=0, max_digits=7),
        ),
    ]
