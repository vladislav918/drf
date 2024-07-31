# Generated by Django 5.0.6 on 2024-07-31 16:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_comment_created_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='readlist',
            constraint=models.UniqueConstraint(fields=('user', 'book'), name='unique_read_list_entry'),
        ),
    ]