# Generated by Django 4.1.6 on 2023-03-30 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_equivalencyrequest_foreign_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='equivalencyrequest',
            name='status',
            field=models.CharField(default='SUBMITTED', max_length=50),
            preserve_default=False,
        ),
    ]
