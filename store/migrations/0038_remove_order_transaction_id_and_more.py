# Generated by Django 5.1.1 on 2024-10-07 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_remove_purchasehistory_discounted_price_at_purchase_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='transaction_id',
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
