# Generated by Django 5.0.6 on 2024-07-09 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_myuser_is_active_myuser_is_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productmodel',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='saledetailmodel',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='saledetailmodel',
            name='subtotal',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='salemodel',
            name='total_price',
            field=models.FloatField(),
        ),
    ]
