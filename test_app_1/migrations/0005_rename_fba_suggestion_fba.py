# Generated by Django 3.2.9 on 2021-12-02 18:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('test_app_1', '0004_fba_suggestion_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FBA_Suggestion',
            new_name='Fba',
        ),
    ]