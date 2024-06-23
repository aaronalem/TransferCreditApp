from app.models import UVACourse, ForeignCourse, ForeignSchool, Equivalency
from django.core.management.base import BaseCommand
from app.management.commands.sis_api_parser import SisApiParser
from app.management.commands.sis_api_parser_previous_semester import SisApiParserPreviousSemester
import pickle

class Command(BaseCommand):
    help = "clears UVA Course table and gets all current UVA Courses"

    def handle(self, *args, **options):
        courses = SisApiParser.getAllCourses()
        with open("courses_data.pkl", "wb") as f:
            pickle.dump(courses, f)
        courses.extend(SisApiParserPreviousSemester.getAllCourses())
        with open("courses_data_2.pkl", "wb") as f:
            pickle.dump(courses, f)
        UVACourse.objects.all().delete()
        for course in courses:
            uva_course = UVACourse(course_id = course['course_id'],
                                   department=course['department'],
                                   catalog_number = course['catalog_number'],
                                   academic_career_description=course['academic_career_description'],
                                   credits=course['credits'],
                                   description=course['description'][:200])
            uva_course.save()
        