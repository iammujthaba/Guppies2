        
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0038_remove_order_transaction_id_and_more'),  # Make sure this is correct
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=100, unique=True, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_signature',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]