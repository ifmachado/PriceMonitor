# Generated by Django 4.0.3 on 2022-10-13 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0021_producttouser_price_email_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttouser',
            name='auth_token',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
