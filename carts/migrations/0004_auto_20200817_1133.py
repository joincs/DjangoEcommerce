# Generated by Django 3.0.8 on 2020-08-17 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_cartitem_lin_item_total'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='lin_item_total',
            new_name='line_item_total',
        ),
    ]
