# Generated by Django 4.2.6 on 2024-02-05 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='status',
            field=models.TextField(blank=True, default='Offline', null=True),
        ),
    ]
