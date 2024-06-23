from bs4 import BeautifulSoup
import requests
from app.models import UVACourse, ForeignCourse, ForeignSchool, Equivalency
from django.core.management.base import BaseCommand, CommandError
import re

EQUIVALENCY_PAGE = "https://engineering.virginia.edu/current-students/current-undergraduate-students/transferring-uva-engineering/transfer-credit"

class Command(BaseCommand):
    help = "populates the relevant tables in the database with engineering course equivalencies"
    
    def handle(self, *args, **options):
        response = request = requests.get(EQUIVALENCY_PAGE)
        state_name = ""
        
        equivalencies = []
        foreign_schools = set()
        foreign_courses = []
        uva_courses = []
        uva_course_names = []
        cur_school = ""
        handling_virginia = False
        read_schools = False
        read_courses = False
        handling_hawaii = False

        if (response.status_code == 200):
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.table
            rows = table.find_all('tr')
            rows.pop(0)
            for row in rows:
                entries = row.find_all('td')
                if handling_hawaii:
                    if entries[0].string.strip() == "ILLINOIS":
                        handling_hawaii = False
                        state_name="ILLINOIS"
                    else:
                        entries = re.split("\s{2,}", entries[0].string)
                        html_string = ""
                        for entry in entries:
                            if entry.strip() == "":
                                html_string += "<p>" + " " + "</p>"
                            else:
                                html_string += "<p>" + entry + "</p>"
                        entries = BeautifulSoup(html_string, 'html.parser').find_all('p')
                if len(entries) == 1 and not handling_virginia:
                    state_name = entries[0].get_text()
                    if state_name.strip() == "VIRGINIA":
                        handling_virginia = True
                    elif state_name.strip() == "HAWAII":
                        handling_hawaii = True
                elif handling_virginia and not read_schools:
                    college_name_pre = entries[0].get_text().split("(")[1]
                    college_names = [name.strip() for name in college_name_pre.split(",")]
                    foreign_schools.update(college_names)
                    read_schools = True
                elif handling_virginia and read_schools and not read_courses:
                    if "PHY 242" in entries[1].get_text().strip():
                        read_courses = True
                        handling_virginia = False
                    if "/" in entries[4].string:
                        catalog_numbers = entries[4].string.split()[1].split("/")
                        if (len(catalog_numbers) != 2):
                            departments = entries[4].string.split()[0].split("/")
                            d1 = departments[0]
                            d2 = departments[1]
                            cnum = entries[4].string.split()[1]
                            credits = int(entries[5].string)

                            foreign_courses.extend([{
                                'department': entries[1].string.split()[0],
                                'catalog_number': entries[1].string.split()[1],
                                'state': state_name,
                                'description': entries[2].string,
                                'credits': credits,
                                'foreign_school': school
                            } for school in college_names])

                            if d1 + " " + cnum not in uva_course_names:
                                uva_courses.append({
                                    'department': d1,
                                    'catalog_number': cnum,
                                    'credits': credits
                                })

                                uva_course_names.append(d1 + " " + cnum)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                                
                            else:
                                position = uva_course_names.index(d1 + " " + cnum)
                                equivalencies.extend([(i, position) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])

                            if d2 + " " + cnum not in uva_course_names:
                                uva_courses.append({
                                    'department': d2,
                                    'catalog_number': cnum,
                                    'credits': credits
                                })

                                uva_course_names.append(d2 + " " + cnum)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                                
                            else:
                                position = uva_course_names.index(d2 + " " + cnum)
                                equivalencies.extend([(i, position) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                        else:
                            cnum1 = catalog_numbers[0]
                            cnum2 = catalog_numbers[1]
                            if (len(entries[5].string.split("/")) == 2):
                                cred1 = int(entries[5].string.split("/")[0])
                                cred2 = int(entries[5].string.split("/")[1])
                            else:
                                cred1 = cred2 = int(entries[5].string)
                            if "/" in entries[3].string:
                                foreign_credits = 3
                            else:
                                foreign_credits = int(entries[3].string)

                            foreign_courses.extend([{
                                'department': entries[1].string.split()[0],
                                'catalog_number': entries[1].string.split()[1],
                                'state': state_name,
                                'description': entries[2].string,
                                'credits': foreign_credits,
                                'foreign_school': school
                            } for school in college_names])

                            department = entries[4].string.split()[0]
                            if department + " " + cnum1 not in uva_course_names:
                                uva_courses.append({
                                    'department': department,
                                    'catalog_number': cnum1,
                                    'credits': cred1
                                })

                                uva_course_names.append(department + " " + cnum1)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                                
                            else:
                                position = uva_course_names.index(department + " " + cnum1)
                                equivalencies.extend([(i, position) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])

                            if department + " " + cnum2 not in uva_course_names:
                                uva_courses.append({
                                    'department':department,
                                    'catalog_number': cnum2,
                                    'credits': cred2
                                })
                                uva_course_names.append(department + " " + cnum2)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                            else:
                                position = uva_course_names.index(department + " " + cnum2)
                                equivalencies.extend([(i, position) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                    else:
                        if "/" in entries[1].string:
                            catalog_numbers = entries[1].string.split()[1].split("/")
                            cnum1 = catalog_numbers[0]
                            cnum2 = catalog_numbers[1]
                            cred1 = int(entries[3].string.split("/")[0])
                            cred2 = int(entries[3].string.split("/")[1])

                            foreign_courses.extend([{
                                'department': entries[1].string.split()[0],
                                'catalog_number': cnum1,
                                'state': state_name,
                                'description': entries[2].string,
                                'credits': cred1,
                                'foreign_school': school
                            } for school in college_names])

                            foreign_courses.extend([{
                                'department': entries[1].string.split()[0],
                                'catalog_number': cnum2,
                                'state': state_name,
                                'description': entries[2].string,
                                'credits': cred2,
                                'foreign_school': school
                            } for school in college_names])

                            if "*" in entries[5].string:
                                uva_credits = int(entries[5].string[:-1])
                            elif entries[5].string.strip() == "" and entries[4].string.strip() == "MAE 2100":
                                uva_credits = 3
                            else:
                                uva_credits = int(entries[5].string)
                            if entries[4].string not in uva_course_names:
                                uva_courses.append({
                                    'department': entries[4].string.split()[0],
                                    'catalog_number': entries[4].string.split()[1],
                                    'credits': uva_credits
                                })
                                uva_course_names.append(entries[4].string)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - 2*len(college_names), len(foreign_courses))])
                            else:
                                index = uva_course_names.index(entries[4].string)
                                equivalencies.extend([(i, index) for i in range(len(foreign_courses) - 2*len(college_names), len(foreign_courses))])
                        else:
                            foreign_courses.extend([{
                                'department': entries[1].string.split()[0],
                                'catalog_number': entries[1].string.split()[1],
                                'state': state_name,
                                'description': entries[2].string,
                                'credits': int(entries[3].string),
                                'foreign_school': school
                            } for school in college_names])

                            if "*" in entries[5].string:
                                uva_credits = int(entries[5].string[:-1])
                            elif entries[5].string.strip() == "" and entries[4].string.strip() == "MAE 2100":
                                uva_credits = 3
                            else:
                                uva_credits = int(entries[5].string)
                            if entries[4].string not in uva_course_names:
                                uva_courses.append({
                                    'department': entries[4].string.split()[0],
                                    'catalog_number': entries[4].string.split()[1],
                                    'credits': uva_credits
                                })
                                uva_course_names.append(entries[4].string)
                                equivalencies.extend([(i, len(uva_courses)-1) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                            else:
                                index = uva_course_names.index(entries[4].string)
                                equivalencies.extend([(i, index) for i in range(len(foreign_courses) - len(college_names), len(foreign_courses))])
                elif entries[1].string.strip() == "":
                    continue
                else:
                    if entries[0].string.strip() != "" and "*" not in entries[0].string:
                        cur_school = entries[0].string
                    if '/' in entries[4].string:
                        catalog_numbers = entries[4].string.split()[1].split("/")
                        cnum1 = catalog_numbers[0]
                        cnum2 = catalog_numbers[1]
                        cred1 = int(entries[5].string.split("/")[0])
                        cred2 = int(entries[5].string.split("/")[1])
                        if entries[3].string.strip() == "":
                            foreign_credits = 4
                        else:
                            foreign_credits = int(entries[3].string)
                        foreign_courses.append({
                            'department': entries[1].string.split()[0],
                            'catalog_number': entries[1].string.split()[1],
                            'state': state_name,
                            'description': entries[2].string,
                            'credits': foreign_credits,
                            'foreign_school': cur_school
                        })
                        foreign_schools.add(cur_school)

                        department = entries[4].string.split()[0]
                        if department + " " + cnum1 not in uva_course_names:
                            uva_courses.append({
                                'department': department,
                                'catalog_number': cnum1,
                                'credits': cred1
                            })

                            uva_course_names.append(department + " " + cnum1)
                            equivalencies.append((len(foreign_courses)-1, len(uva_courses)-1))
                            
                        else:
                            position1 = uva_course_names.index(department + " " + cnum1)
                            equivalencies.append((len(foreign_courses)-1, position1))

                        if department + " " + cnum2 not in uva_course_names:
                            uva_courses.append({
                                'department':department,
                                'catalog_number': cnum2,
                                'credits': cred2
                            })
                            uva_course_names.append(department + " " + cnum2)
                            equivalencies.append((len(foreign_courses)-1, len(uva_courses)-1))
                        else:
                            position = uva_course_names.index(department + " " + cnum2)
                            equivalencies.append((len(foreign_courses)-1, position))
                                                         

                    else:
                        if entries[3].string.strip() == "":
                            foreign_credits = 4
                        else:
                            foreign_credits = int(entries[3].string)
                        foreign_courses.append({
                            'department': entries[1].string.split()[0],
                            'catalog_number': entries[1].string.split()[1],
                            'state': state_name,
                            'description': entries[2].string,
                            'credits': foreign_credits,
                            'foreign_school': cur_school
                        })
                        foreign_schools.add(cur_school)

                        if "*" in entries[5].string:
                            uva_credits = int(entries[5].string[:-1])
                        elif entries[5].string.strip() == "" and entries[4].string.strip() == "MAE 2100":
                            uva_credits = 3
                        else:
                            uva_credits = int(entries[5].string)
                        if entries[4].string not in uva_course_names:
                            uva_courses.append({
                                'department': entries[4].string.split()[0],
                                'catalog_number': entries[4].string.split()[1],
                                'credits': uva_credits
                            })
                            uva_course_names.append(entries[4].string)
                            #append index of foreign course, index of uva course
                            equivalencies.append((len(foreign_courses)-1, len(uva_courses)-1))
                        else:
                            position = uva_course_names.index(entries[4].string)
                            equivalencies.append((len(foreign_courses)-1, position))

            uva_course_objects = []
            for course in uva_courses:
                if UVACourse.objects.filter(department=course['department'], catalog_number = course['catalog_number']).exists():
                    uva_course = UVACourse.objects.get(department=course['department'], catalog_number = course['catalog_number'])
                else:
                    i = 10000
                    while UVACourse.objects.filter(course_id=i).exists():
                        i+= 1
                    uva_course = UVACourse(course_id = i,
                                   department=course['department'],
                                   catalog_number = course['catalog_number'],
                                   academic_career_description="Undergraduate",
                                   credits=course['credits'],
                                   description="No description.")
                    uva_course.save()
                uva_course_objects.append(uva_course)

            for school_name in foreign_schools:
                if not ForeignSchool.objects.filter(name=school_name).exists():
                    foreign_school = ForeignSchool(name=school_name)
                    foreign_school.save()

            foreign_course_objects = []
            
            for course in foreign_courses:
                foreign_school = ForeignSchool.objects.get(name=course['foreign_school'])
                foreign_course = ForeignCourse(department = course['department'],
                                        catalog_number = course['catalog_number'],
                                        description = course['description'],
                                        foreign_school = foreign_school,
                                        credits = course['credits'])
                foreign_course_objects.append(foreign_course)
                foreign_course.save()
            
            for equivalency in equivalencies:
                foreign_course = foreign_course_objects[equivalency[0]]
                uva_course = uva_course_objects[equivalency[1]]
                equivalency = Equivalency(uva_course = uva_course,
                                    foreign_course = foreign_course)
                equivalency.save()
