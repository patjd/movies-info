# Generated by Django 4.0.2 on 2022-04-04 05:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_order_email_order_first_name_order_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
