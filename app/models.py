from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.
# class Choice(models.Model):
#   question = models.ForeignKey(Question, on_delete=models.CASCADE)
#   choice_text = models.CharField(max_length=200)
#   votes = models.IntegerField(default=0)

#   def __str__(self):
#     return self.choice_text

class UVACourse(models.Model):
    course_id = models.IntegerField(primary_key=True)

    department = models.CharField(max_length=10)
    catalog_number = models.CharField(max_length=20)
    academic_career_description = models.CharField(max_length=50)
    credits = models.CharField(max_length=20)
    # not actual description but name of the course, e.g. "Introduction to Programming"
    description = models.CharField(max_length=200)

class ForeignSchool(models.Model):
    name = models.CharField(max_length=100)

class ForeignCourse(models.Model):
    department = models.CharField(max_length=10)
    catalog_number = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    foreign_school = models.ForeignKey(ForeignSchool, on_delete=models.CASCADE)
    credits = models.CharField(max_length=20)

class Equivalency(models.Model):
    uva_course = models.ForeignKey(UVACourse, on_delete=models.CASCADE)
    foreign_course = models.ForeignKey(ForeignCourse, on_delete=models.CASCADE)

class EquivalencyAdmin(admin.ModelAdmin):
    search_fields = ['uva_course__catalog_number']

class EquivalencyRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uva_course = models.ForeignKey(UVACourse, on_delete=models.CASCADE)
    foreign_school = models.CharField(max_length=100)
    foreign_course_department = models.CharField(max_length=10)
    foreign_course_catalog_number = models.CharField(max_length=10)
    foreign_course_credits = models.CharField(max_length=20)
    foreign_course_url = models.CharField(max_length=512)
    foreign_course_description = models.CharField(max_length=512)
    status = models.CharField(max_length=50)
    comment = models.CharField(max_length=512)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
