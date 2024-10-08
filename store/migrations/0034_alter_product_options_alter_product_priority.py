# Generated by Django 5.1.1 on 2024-09-18 11:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_product_priority'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['priority', 'name']},
        ),
        migrations.AlterField(
            model_name='product',
            name='priority',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
