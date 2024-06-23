from app.models import UVACourse, ForeignCourse, ForeignSchool, Equivalency
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "clears transfer equivalency information databases"

    def handle(self, *args, **options):
        ForeignCourse.objects.all().delete()
        ForeignSchool.objects.all().delete()
        Equivalency.objects.all().delete()