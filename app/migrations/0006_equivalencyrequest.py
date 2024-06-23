# Generated by Django 4.1.6 on 2023-03-30 05:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0005_alter_foreigncourse_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquivalencyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foreign_school', models.CharField(max_length=100)),
                ('foreign_course_department', models.CharField(max_length=10)),
                ('foreign_course_catalog_number', models.CharField(max_length=10)),
                ('foreign_course_credits', models.CharField(max_length=20)),
                ('foreign_course_url', models.CharField(max_length=200)),
                ('foreign_course_description', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('uva_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.uvacourse')),
            ],
        ),
    ]
