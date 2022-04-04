# Generated by Django 4.0.2 on 2022-04-04 16:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0008_alter_order_order_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cast',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cast',
            name='birthday',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='cast',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 4, 12, 39, 56, 615280)),
        ),
    ]