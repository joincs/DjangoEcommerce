# Generated by Django 3.0.8 on 2020-08-18 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0006_auto_20200818_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='tax_percentage',
            field=models.DecimalField(decimal_places=5, default=0.085, max_digits=10),
        ),
    ]
