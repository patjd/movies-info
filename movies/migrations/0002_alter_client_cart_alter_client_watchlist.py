# Generated by Django 4.0.3 on 2022-03-28 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='cart',
            field=models.ManyToManyField(blank=True, related_name='cart', to='movies.movie'),
        ),
        migrations.AlterField(
            model_name='client',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='movies.movie'),
        ),
    ]
