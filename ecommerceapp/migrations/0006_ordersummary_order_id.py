# Generated by Django 5.1.7 on 2025-05-27 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0005_remove_ordersummary_book_object_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordersummary',
            name='order_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
