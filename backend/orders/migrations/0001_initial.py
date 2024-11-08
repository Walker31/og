# Generated by Django 5.1.2 on 2024-10-29 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('address', models.CharField(max_length=511)),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order_status', models.CharField(max_length=255)),
                ('payment_type', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'orders',
                'managed': False,
            },
        ),
    ]