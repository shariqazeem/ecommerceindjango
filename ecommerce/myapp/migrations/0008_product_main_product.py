# Generated by Django 5.0.2 on 2024-03-26 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_product_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='main_product',
            field=models.BooleanField(default=False),
        ),
    ]
