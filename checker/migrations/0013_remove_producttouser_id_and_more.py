# Generated by Django 4.0.3 on 2022-09-30 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0012_producttouser_id_alter_producttouser_auth_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producttouser',
            name='id',
        ),
        migrations.AlterField(
            model_name='producttouser',
            name='auth_token',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]
