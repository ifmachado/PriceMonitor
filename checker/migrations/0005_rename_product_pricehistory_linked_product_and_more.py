# Generated by Django 4.0.3 on 2022-09-29 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0004_alter_product_product_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pricehistory',
            old_name='product',
            new_name='linked_product',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='product',
            new_name='linked_product',
        ),
        migrations.AlterField(
            model_name='pricehistory',
            name='price',
            field=models.IntegerField(null=True),
        ),
    ]
