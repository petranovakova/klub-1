# Generated by Django 2.1.2 on 2018-12-11 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0012_auto_20181114_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='telephone',
            name='is_primary',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]