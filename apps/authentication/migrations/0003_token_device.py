# Generated by Django 4.2.5 on 2023-09-13 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_token_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='device',
            field=models.CharField(default='unknown', max_length=250),
        ),
    ]
