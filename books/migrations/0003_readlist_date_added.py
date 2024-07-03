# Generated by Django 5.0.6 on 2024-07-02 16:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_readlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='readlist',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
