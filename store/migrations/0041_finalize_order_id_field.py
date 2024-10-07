from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0040_populate_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=100, unique=True),
        ),
    ]