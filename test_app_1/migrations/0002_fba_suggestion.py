# Generated by Django 3.2.9 on 2021-12-02 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('test_app_1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FBA_Suggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plain_carton_line_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test_app_1.plain_carton_line_item')),
            ],
        ),
    ]
