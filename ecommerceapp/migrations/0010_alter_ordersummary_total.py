# Generated by Django 5.1.7 on 2025-05-28 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0009_alter_deliverydetails_pincode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersummary',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]
