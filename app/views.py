from django.http import *
from django.shortcuts import render, redirect
from django.urls import reverse
import yaml
from .data import *
from .models import *
import requests
from datetime import datetime
import re
from django.core.paginator import Paginator
from django.contrib import messages
from django import template

register = template.Library()


def index(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/google/login")
    else:
        if is_admin(request.user):
            return redirect(reverse("dashboard"))
        else:
            return redirect(reverse("search"))


def dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access that page.")
        return redirect(reverse("index"))
    if is_admin(request.user):
        return render(request, 'app/admin_dashboard.html', {'equivalency_requests': EquivalencyRequest.objects.filter(status="UNDER_REVIEW")})
    else:
        return redirect(reverse("index"))

@register.filter
def is_admin(user):
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        with open("admins.yaml", 'r') as stream:
            try:
                admins = yaml.safe_load(stream)['admins']
                if user.email in admins:
                    profile.is_admin = True
                else:
                    profile.is_admin = False
            except yaml.YAMLError as exc:
                print(exc)
        profile.save()
    return profile.is_admin

# def sisapi(request): #this is for testing
    # return HttpResponse('","'.join(SisApiParser.getDepMnemonics()))
    # return HttpResponse(' '.join(SisApiParser.getAllCoursesFromDep("CS")))
    # return HttpResponse(str(SisApiParser.getCourseExists("cs", 1110)) + " " + str(SisApiParser.getCourseExists("cs", 0)))


def equivalencies(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access that page.")
        return redirect(reverse("index"))
    foreign_school_name = request.GET.get('foreign_school_name')
    foreign_course = request.GET.get('foreign_course')
    foreign_description = request.GET.get('foreign_description')
    foreign_credits = request.GET.get('foreign_credits')
    uva_course_description = request.GET.get('uva_course_description')
    uva_course_credits = request.GET.get('uva_course_credits')
    uva_course = request.GET.get('course')
    error_msg = ""
    if not (foreign_school_name or foreign_course or foreign_description or foreign_credits
            or uva_course_description or uva_course_credits or uva_course):
        messages.error(
            request, "No query parameters provided. Please provide the parameters to search with.")
        return redirect(search)
    equivalencies = Equivalency.objects.all()
    if foreign_school_name:
        equivalencies = equivalencies.filter(
            foreign_course__foreign_school__name__icontains=foreign_school_name)
    if foreign_description:
        equivalencies = equivalencies.filter(
            foreign_course__description__icontains=foreign_description)
    if foreign_credits:
        equivalencies = equivalencies.filter(
            foreign_course__credits=foreign_credits)
    if uva_course_description:
        equivalencies = equivalencies.filter(
            uva_course__description__icontains=uva_course_description)
    if uva_course_credits:
        equivalencies = equivalencies.filter(
            uva_course__credits=uva_course_credits)
    if uva_course:
        uva_course_parts = uva_course.split()
        if len(uva_course_parts) != 2:
            messages.error(
                request, "The provided UVA course format is incorrect. Please format it with the department and catalog number separated by a space (e.g. CS 1110).")
            return redirect(search)
        uva_dep = uva_course_parts[0].upper()
        uva_num = uva_course_parts[1]
        uvaCourse = UVACourse.objects.filter(
            department=uva_dep).filter(catalog_number=uva_num)
        if len(uvaCourse) == 0:
            messages.error(request, "The provided UVA course doesn't exist.")
            return redirect(search)
        equivalencies = equivalencies.filter(uva_course=uvaCourse[0])
    if foreign_course:
        foreign_course_parts = foreign_course.split()
        if len(foreign_course_parts) != 2:
            messages.error(
                request, "The provided transfer course format is incorrect. Please format it with the department and catalog number separated by a space (e.g. CS 1110).")
            return redirect(search)
        uva_dep = foreign_course_parts[0].upper()
        uva_num = foreign_course_parts[1]
        foreign_course = ForeignCourse.objects.filter(
            department=uva_dep).filter(catalog_number=uva_num)
        if len(foreign_course) == 0:
            messages.error(
                request, "The provided transfer course does not exist.")
            return redirect(search)
        equivalencies = equivalencies.filter(foreign_course__in=foreign_course)
    equivalencies = equivalencies.order_by("id")
    if len(equivalencies) == 0:
        messages.error(
            request, "The given search parameters did not return any equivalencies. Please revise your search parameters.")
        return redirect(search)
    # https://docs.djangoproject.com/en/4.2/topics/pagination/ for how to implement pagination in Django
    paginator = Paginator(equivalencies, 25)
    page_number = request.GET.get("page")
    equivalencies = paginator.get_page(page_number)
    return render(request, 'app/equivalencies.html', {'courses': getCourses(), 'error_msg': error_msg, 'equivalencies': equivalencies})


def request(request):
    if not request.user.is_authenticated:
        messages.error(
            request, "You must be logged into make an equivalency request.")
        return redirect(reverse("index"))
    return render(request, 'app/request.html', {'courses': getCourses()})


def addRequest(request):
    if not request.user.is_authenticated:
        messages.error(
            request, "You must be logged into make an equivalency request.")
        return redirect(reverse("index"))
    user = request.user
    # print("POST")
    # print(request.POST)

    if 'uvaCourse' not in request.POST:
        return redirect(reverse("search"))
    if 'foreignSchool' not in request.POST:
        return redirect(reverse("search"))
    if 'foreignCourse' not in request.POST:
        return redirect(reverse("search"))
    if 'foreignCourseCredits' not in request.POST:
        return redirect(reverse("search"))
    if 'foreignCourseURL' not in request.POST:
        return redirect(reverse("search"))
    if 'foreignCourseDescription' not in request.POST:
        return redirect(reverse("search"))

    uvaCourse = request.POST['uvaCourse']
    foreignSchool = request.POST['foreignSchool']
    foreignCourse = request.POST['foreignCourse']
    foreignCourseCredits = request.POST['foreignCourseCredits']
    foreignCourseURL = request.POST['foreignCourseURL']
    foreignCourseDescription = request.POST['foreignCourseDescription']

    uvaCourse = uvaCourse.split()
    if len(uvaCourse) != 2:
        messages.error(request, "Invalid UVA Course Name Format")
        return render(request, 'app/request.html')
    else:
        dep = uvaCourse[0].upper()
        catNum = uvaCourse[1]
        uvaCourse = UVACourse.objects.filter(
            department=dep).filter(catalog_number=catNum)
        if len(uvaCourse) == 0:
            messages.error(request, "The provided UVA Course does not exist.")
            return render(request, 'app/request.html')

    foreignCourse = foreignCourse.split()
    if len(foreignCourse) != 2:
        messages.error(request, "Invalid Transfer Course Name Format")
        return render(request, 'app/request.html')

    uvaCourse = uvaCourse[0]
    foreignCourseDep = foreignCourse[0].upper()
    foreignCourseCatNum = foreignCourse[1]

    EquivalencyRequest.objects.create(user=user, uva_course=uvaCourse, foreign_school=foreignSchool, foreign_course_department=foreignCourseDep, foreign_course_catalog_number=foreignCourseCatNum,
                                      foreign_course_credits=foreignCourseCredits, foreign_course_url=foreignCourseURL, foreign_course_description=foreignCourseDescription, status="UNDER_REVIEW")

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        with open("admins.yaml", 'r') as stream:
            try:
                admins = yaml.safe_load(stream)['admins']
                if request.user.email in admins:
                    profile.is_admin = True
                else:
                    profile.is_admin = False
            except yaml.YAMLError as exc:
                print(exc)
        profile.save()
    messages.success(request, "Equivalency request successfully submitted!")
    if profile.is_admin:
        return redirect(reverse('dashboard'))
    else:
        return redirect(reverse('viewallrequests'))


def viewRequest(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view requests.")
        return redirect(reverse("index"))

    equivalency_request = EquivalencyRequest.objects.get(id=id)
    # print(equivalency_request)
    return render(request, 'app/viewrequest.html', {'request': equivalency_request})


def viewAllRequests(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view requests.")
        return redirect(reverse("index"))
    equivalencies = {}
    profile = request.user.profile
    if profile.is_admin:
        equivalencies = EquivalencyRequest.objects.all()
    else:
        equivalencies = EquivalencyRequest.objects.filter(user=profile.user)
    return render(request, 'app/viewallrequests.html', {'equivalencies': equivalencies})


def update_request(request):
    if not request.user.is_authenticated or not is_admin(request.user):
        messages.error(
            request, "You must be logged in to an admin account to update requests.")
        return redirect(reverse("index"))

    if 'id' not in request.POST:
        return redirect(reverse("dashboard"))
    if 'action' not in request.POST:
        return redirect(reverse("dashboard"))
    if 'comment' not in request.POST:
        return redirect(reverse("dashboard"))

    id = request.POST['id']
    status = request.POST['action']
    comments = request.POST['comment']

    equivalency_request = EquivalencyRequest.objects.get(id=id)
    if(status == "APPROVED"):
        foreignSchool = ForeignSchool.objects.filter(
            name=equivalency_request.foreign_school)
        if len(foreignSchool) == 0:
            foreignSchool = ForeignSchool.objects.create(
                name=equivalency_request.foreign_school)
        else:
            foreignSchool = foreignSchool[0]
        foreignCourse = ForeignCourse.objects.create(department=equivalency_request.foreign_course_department, catalog_number=equivalency_request.foreign_course_catalog_number,
                                                     description=equivalency_request.foreign_course_description, foreign_school=foreignSchool, credits=equivalency_request.foreign_course_credits)
        Equivalency.objects.create(
            foreign_course=foreignCourse, uva_course=equivalency_request.uva_course)
        equivalency_request.status = "APPROVED"
        equivalency_request.comment = comments
        equivalency_request.save()
        messages.success(request, "Equivalency request successfully approved!")
        # print("APPROVED")
    elif(status == "DENIED"):
        equivalency_request.status = "DENIED"
        equivalency_request.comment = comments
        equivalency_request.save()
        messages.success(request, "Equivalency request successfully denied!")
        # print("DENIED")
    return redirect(reverse("dashboard"))


def search(request):
    if request.user.is_authenticated:
        return render(request, 'app/search.html', {'courses': getCourses()})
    messages.error(request, "You must be logged in to access that page.")
    return redirect('index')


def viewCourseInfo(request, department, catalog_number):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to access that page.")
        return redirect(reverse("index"))
    # subject=
    # catalog_nbr=
    baseURL = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1232"
    URL = baseURL + "&subject=" + department + \
        "&catalog_nbr=" + str(catalog_number)
    r = requests.get(URL)
    json = r.json()
    if (len(json) == 0):
        return render(request, 'app/courseinfo.html', {'courseinfo': {'department': department, 'catalog_number': catalog_number, 'description': None}})
    description = json[0]['descr']
    offerings = [{
        'instructors': course['instructors'],
        'meetings': course['meetings'],
        'enrollment': course['enrollment_total'],
        'capacity': course['class_capacity'],
        'waitlist': course['wait_tot'],
        'waitlist_cap': course['wait_cap'],
        'instruction_mode_description': course['instruction_mode_descr'],
        'section_type': course['section_type']
    } for course in json]
    weekdays = {
        'Mo': 'Monday',
        'Tu': 'Tuesday',
        'We': 'Wednesday',
        'Th': 'Thursday',
        'Fr': 'Friday',
        'Sa': 'Saturday',
        'Su': 'Sunday',
    }
    for offering in offerings:
        for meeting in offering['meetings']:
            if meeting['days'] != '-':
                meeting['start_time'] = datetime.strptime(
                    meeting['start_time'], '%H.%M.%S.%f%z')
                meeting['end_time'] = datetime.strptime(
                    meeting['end_time'], '%H.%M.%S.%f%z')
                days = re.findall('[A-Z][^A-Z]*', meeting['days'])
                meeting['days'] = ', '.join(weekdays[day] for day in days)
            else:
                meeting['start_time'] = 'N/A'
                meeting['end_time'] = 'N/A'
                meeting['days'] = 'N/A'
    return render(request, 'app/courseinfo.html', {'courseinfo': {'department': department, 'catalog_number': catalog_number, 'description': description}, 'offerings': offerings})


def handler404(request, exception):
    return render(request, 'app/404.html', {}, status=404)


def handler500(request):
    return render(request, 'app/500.html', {}, status=500)


def handler400(request, exception):
    return render(request, 'app/400.html', {}, status=400)
