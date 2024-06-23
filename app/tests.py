from django.test import TestCase
from django.urls import reverse
from .models import *
from app.management.commands.sis_api_parser import SisApiParser
from django.contrib.auth.models import User

class SisApiParserTests(TestCase):

    def test_getCourseExists_true(self):
        """
        getCourseExists() returns true for valid course.
        """
        self.assertIs(SisApiParser.getCourseExists("CS", 1110), True)

    def test_getCourseExists_false(self):
        """
        getCourseExists() returns false for invalid course.
        """
        self.assertIs(SisApiParser.getCourseExists("CS", 0), False)

class DatabaseModelTests(TestCase):
    def test_createUVACourse(self):
        """
        should create 1 UVACourse successfully
        """
        course = UVACourse.objects.create(course_id = 123, department = "APMA", catalog_number = 2120, academic_career_description = "ENGR", credits=4, description = "math")
        self.assertEqual(len(UVACourse.objects.all()), 1)

    def test_createForeignSchool(self):
        """
        should create 1 Foreign School successfully
        """
        school = ForeignSchool.objects.create(name = "University of Pennsylvania")
        self.assertEqual(len(ForeignSchool.objects.all()), 1)

    def test_createForeignCourse(self):
        """
        should create 1 Foreign Course successfully
        """
        foreignSchool = ForeignSchool.objects.create(name = "University of Pennsylvania")
        foreignCourse = ForeignCourse.objects.create(department = "MATH", catalog_number = 103, credits = 4, description = "math", foreign_school = foreignSchool)
        self.assertEqual(len(ForeignSchool.objects.all()), 1)
        self.assertEqual(len(ForeignCourse.objects.all()), 1)

    def test_createEquivalency(self):
        """
        should create 1 Equivalency successfully
        """
        course = UVACourse.objects.create(course_id = 123, department = "APMA", catalog_number = 2120, academic_career_description = "ENGR", credits=4, description = "math")
        foreignSchool = ForeignSchool.objects.create(name = "University of Pennsylvania")
        foreignCourse = ForeignCourse.objects.create(department = "MATH", catalog_number = 103, credits = 4, description = "math", foreign_school = foreignSchool)
        eqv = Equivalency.objects.create(uva_course = course, foreign_course = foreignCourse)
        self.assertEqual(len(Equivalency.objects.all()), 1)

class LoginAdminTests(TestCase):
    def setUp(self):
        admin = User(email="admin@gmail.com", username="an_admin", password="pass")
        admin.save()
        profile = Profile(user=admin, is_admin=True)
        profile.save()
        user = User(email="user@gmail.com", username="a_user", password="pass")
        student = User(email="cs3240.student@gmail.com", username="cs3240student", password="test")
        student.save()
        super = User(email="cs3240.super@gmail.com", username="cs3240super", password="test2")
        user.save()
        super.save()
        profile2 = Profile(user=user)
        profile2.save()

    def test_known_admin_is_admin(self):
        admin = User.objects.get(email="admin@gmail.com")
        profile = admin.profile
        self.assertTrue(profile.is_admin)
    
    def test_not_admin_isnt_admin(self):
        user = User.objects.get(email="user@gmail.com")
        profile = user.profile
        self.assertFalse(profile.is_admin)

    def test_student_account_isnt_admin(self):
        user = User.objects.get(email="cs3240.student@gmail.com")
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertContains(response, "Equivalency Search")
        

    def test_super_account_is_admin(self):
        user = User.objects.get(email="cs3240.super@gmail.com")
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Welcome to your dashboard, cs3240super!")

    def test_AdminDashboard(self):
        admin = User.objects.get(email="admin@gmail.com")
        self.client.force_login(admin)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Welcome to your dashboard, an_admin!")

class SearchTests(TestCase):
    def setUp(self):
        foreign_school = ForeignSchool(name="College of William and Mary")
        foreign_school.save()
        foreign_course = ForeignCourse(department="CSCI", catalog_number="301", foreign_school=foreign_school, description="A CS course", credits=3)
        foreign_course.save()
        uva_course = UVACourse(course_id=1, department="CS", catalog_number="3240", description="Advanced Software Development Essentials", credits = 4)
        uva_course.save()
        equivalency = Equivalency(uva_course=uva_course, foreign_course=foreign_course)
        equivalency.save()
        user = User(email="user@gmail.com", username="a_user", password="pass")
        user.save()
        self.client.force_login(user)

    def test_search_results_no_parameters(self):
        response = self.client.get(reverse('equivalencies'), follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "No query parameters provided. Please provide the parameters to search with.")

    def test_search_results_cs_3240(self):
        response = self.client.get(reverse('equivalencies') + "?course=CS+3240")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_bad_course(self):
        response = self.client.get(reverse('equivalencies') + "?course=CS+3241", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The provided UVA course doesn&#x27;t exist.")


    def test_search_results_school_substring(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_bad_substring(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=willim", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The given search parameters did not return any equivalencies. Please revise your search parameters.")

    def test_search_results_foreign_description(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_description=cs")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_bad_foreign_description(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_description=hehe", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The given search parameters did not return any equivalencies. Please revise your search parameters.")

    def test_search_results_foreign_credits(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_credits=3")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_foreign_credits_bad(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_credits=4", follow = True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The given search parameters did not return any equivalencies. Please revise your search parameters.")

    def test_search_results_uva_course_description(self):
        response = self.client.get(reverse('equivalencies') + "?uva_course_description=software")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_uva_course_description_bad(self):
        response = self.client.get(reverse('equivalencies') + "?uva_course_description=sde", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The given search parameters did not return any equivalencies. Please revise your search parameters.")

    def test_search_results_bad_course_format(self):
        response = self.client.get(reverse('equivalencies') + "?course=Hello", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The provided UVA course format is incorrect. Please format it with the department and catalog number separated by a space (e.g. CS 1110).")

    def test_search_results_bad_foreign_course_format(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_course=Hello", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The provided transfer course format is incorrect. Please format it with the department and catalog number separated by a space (e.g. CS 1110).")

    def test_search_results_foreign_course(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_course=CSCI+301")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_bad_foreign_course_name(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_course=CS+302", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The provided transfer course does not exist.")

    def test_search_results_uva_credits(self):
        response = self.client.get(reverse('equivalencies') + "?uva_course_credits=4")
        self.assertNotContains(response, "Equivalency Search")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        self.assertContains(response, "301")

    def test_search_results_bad_uva_credits(self):
        response = self.client.get(reverse('equivalencies') + "?uva_course_credits=3", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The given search parameters did not return any equivalencies. Please revise your search parameters.")


class PaginationTest(TestCase):
    def setUp(self):
        foreign_school = ForeignSchool(name="College of William and Mary")
        foreign_school.save()
        user = User(email="user@gmail.com", username="a_user", password="pass")
        user.save()
        self.client.force_login(user)
        for i in range(1, 1001):
            foreign_course = ForeignCourse(department="CSCI", catalog_number=str(i), foreign_school=foreign_school, description="A CS course " + str(i), credits=3)
            foreign_course.save()
            uva_course = UVACourse(course_id=i, department="CS", catalog_number=str(i), description="Advanced Software Development Essentials " + str(i))
            uva_course.save()
            equivalency = Equivalency(uva_course=uva_course, foreign_course=foreign_course)
            equivalency.save()

    def test_search_bad_request(self):
        response = self.client.get(reverse('equivalencies') + "?course=CS+1001", follow=True)
        self.assertContains(response, "Equivalency Search")
        self.assertContains(response, "The provided UVA course doesn&#x27;t exist.")

    def test_search_no_page(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        for i in range(1, 26):
            self.assertContains(response, "CSCI " + str(i))

    def test_search_page_1(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william&page=1")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        for i in range(1, 26):
            self.assertContains(response, "CSCI " + str(i))

    def test_search_page_40(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william&page=40")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        for i in range(976, 1001):
            self.assertContains(response, "CSCI " + str(i))

    def test_search_page_41(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william&page=41")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        for i in range(976, 1001):
            self.assertContains(response, "CSCI " + str(i))

    def test_search_bad_page(self):
        response = self.client.get(reverse('equivalencies') + "?foreign_school_name=william&page=hello")
        self.assertContains(response, "College of William and Mary")
        self.assertContains(response, "CSCI")
        for i in range(1, 26):
            self.assertContains(response, str(i))

class RequestEquivalencyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user@gmail.com', password='pass')
        profile = Profile.objects.create(user=self.user)
        profile.is_admin = False
        profile.save()
        uva_course = UVACourse.objects.create(department="CS", catalog_number = "3140")

    description = models.CharField(max_length=200)

    def test_request_equivalency_not_signed_in(self):
        response = self.client.get(reverse('addRequest'), follow=True)
        self.assertContains(response, "You must be logged into make an equivalency request.")

    def test_request_equivalency_signed_in(self):
       self.client.login(username='user@gmail.com', password='pass')
       UVACourse.objects.create(department="CS", catalog_number = "3140")
       data = {
           'uvaCourse': 'CS 3140', 
           'foreignSchool': 'VTech', 
           'foreignCourse': 'CS 311',
           'foreignCourseCredits': '3',
           'foreignCourseURL': 'www.url.com',
           'foreignCourseDescription': "test"
       }
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       response = self.client.post(reverse('addRequest'), data)
       self.assertEquals(1, len(EquivalencyRequest.objects.all()))
       self.assertEquals("UNDER_REVIEW", EquivalencyRequest.objects.all()[0].status)

    def test_request_equivalency_wrong_uva_course_format(self):
       self.client.login(username='user@gmail.com', password='pass')
       UVACourse.objects.create(department="CS", catalog_number = "3140")
       data = {
           'uvaCourse': 'CS3140', 
           'foreignSchool': 'VTech', 
           'foreignCourse': 'CS 311',
           'foreignCourseCredits': '3',
           'foreignCourseURL': 'www.url.com',
           'foreignCourseDescription': "test"
       }
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       response = self.client.post(reverse('addRequest'), data)
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       self.assertContains(response, "Invalid UVA Course Name Format")

    def test_request_equivalency_wrong_foreign_course_format(self):
       self.client.login(username='user@gmail.com', password='pass')
       UVACourse.objects.create(department="CS", catalog_number = "3140")
       data = {
           'uvaCourse': 'CS 3140', 
           'foreignSchool': 'VTech', 
           'foreignCourse': 'CS311',
           'foreignCourseCredits': '3',
           'foreignCourseURL': 'www.url.com',
           'foreignCourseDescription': "test"
       }
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       response = self.client.post(reverse('addRequest'), data)
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       self.assertContains(response, "Invalid Transfer Course Name Format")

    def test_request_equivalency_invalid_uva_course(self):
       self.client.login(username='user@gmail.com', password='pass')
       UVACourse.objects.create(department="CS", catalog_number = "3140")
       data = {
           'uvaCourse': 'CS 2100', 
           'foreignSchool': 'VTech', 
           'foreignCourse': 'CS 311',
           'foreignCourseCredits': '3',
           'foreignCourseURL': 'www.url.com',
           'foreignCourseDescription': "test"
       }
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       response = self.client.post(reverse('addRequest'), data)
       self.assertEquals(0, len(EquivalencyRequest.objects.all()))
       self.assertContains(response, "The provided UVA Course does not exist.")

    def test_no_requests__view(self):
        self.client.login(username='user@gmail.com', password='pass')
        response = self.client.get(reverse('viewallrequests'))
        self.assertContains(response, "No Prior Requests.")

    def test_view_all_requests(self):
        self.client.login(username='user@gmail.com', password='pass')
        UVACourse.objects.create(department="CS", catalog_number = "3140")
        data = {
            'uvaCourse': 'CS 3140', 
            'foreignSchool': 'VTech', 
            'foreignCourse': 'CS 311',
            'foreignCourseCredits': '3',
            'foreignCourseURL': 'www.url.com',
            'foreignCourseDescription': "test"
        }
        self.client.post(reverse('addRequest'), data)
        response = self.client.get(reverse('viewallrequests'))
        self.assertContains(response, "CS 3140")
        self.assertContains(response, "Under Review")
    
    def test_view_requests(self):
        self.client.login(username='user@gmail.com', password='pass')
        UVACourse.objects.create(department="CS", catalog_number = "3140")
        data = {
            'uvaCourse': 'CS 3140', 
            'foreignSchool': 'VTech', 
            'foreignCourse': 'CS 311',
            'foreignCourseCredits': '3',
            'foreignCourseURL': 'www.url.com',
            'foreignCourseDescription': "test"
        }
        self.client.post(reverse('addRequest'), data)
        response = self.client.get(reverse('viewrequest', kwargs={'id':1}))
        self.assertContains(response, "CS 3140")
        self.assertContains(response, "test")
        self.assertContains(response, "Under Review")




