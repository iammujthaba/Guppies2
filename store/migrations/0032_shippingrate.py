# Generated by Django 5.1.1 on 2024-09-11 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_alter_orderitem_price_at_purchase_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=100, unique=True)),
                ('base_rate', models.DecimalField(decimal_places=2, max_digits=6)),
                ('additional_item_rate', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
