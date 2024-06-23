from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(UVACourse)
admin.site.register(ForeignSchool)
admin.site.register(ForeignCourse)
admin.site.register(Equivalency, EquivalencyAdmin)
admin.site.register(EquivalencyRequest)
admin.site.register(Profile)