# Generated by Django 5.1.2 on 2024-11-14 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_address_table_alter_customer_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Customer', 'verbose_name_plural': 'Customers'},
        ),
        migrations.AlterModelTable(
            name='address',
            table='address',
        ),
    ]
