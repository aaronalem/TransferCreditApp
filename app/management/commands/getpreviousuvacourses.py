from app.models import UVACourse, ForeignCourse, ForeignSchool, Equivalency
from django.core.management.base import BaseCommand
from app.management.commands.sis_api_parser_previous_semester import SisApiParserPreviousSemester

class Command(BaseCommand):
    help = "gets all previous semester UVA Courses"

    def handle(self, *args, **options):
        courses = SisApiParserPreviousSemester.getAllCourses()
        for course in courses:
            if not UVACourse.objects.filter(course_id=course['course_id']).exists():
                uva_course = UVACourse(course_id = course['course_id'],
                                    department=course['department'],
                                    catalog_number = course['catalog_number'],
                                    academic_career_description=course['academic_career_description'],
                                    credits=course['credits'],
                                    description=course['description'])
                uva_course.save()