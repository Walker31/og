# Generated by Django 5.1.2 on 2024-10-27 04:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_alter_cart_customer_id_alter_cart_product_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'managed': False},
        ),
    ]
