from .models import *

def getCourses():
    courses = []
    for course in UVACourse.objects.all():
        courses.append(course.department.upper() + " " + course.catalog_number)
    courses.sort()
    return courses