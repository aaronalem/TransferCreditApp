from .sis_api_requests import SisApi
from app.models import UVACourse

class SisApiParser:
    def getDepMnemonics():
        depMnemonics = []
        depMnemonicsJson = SisApi.requestDepMnemonics()
        for subject in depMnemonicsJson['subjects']:
            depMnemonics.append(subject['subject'])
        #print(depMnemonics)
        return depMnemonics
    
    def getCoursesFromDepByPage(dep, page):
        dep = dep.upper()
        courses = []
        course_ids = set()
        coursesJson = SisApi.requestCoursesFromDep(dep,page)
        for course in coursesJson:
            course_id = int(course['crse_id'])
            if course_id not in course_ids:
                courses.append({
                        'course_id': course_id,
                        'department': course['subject'],
                        'catalog_number': course['catalog_nbr'],
                        'academic_career_description': course['acad_career_descr'],
                        'credits': course['units'],
                        'description': course['descr']
                    })
                course_ids.add(course_id)
        return courses
    
    def getAllCoursesFromDep(dep):
        dep = dep.upper()
        courses = []
        course_ids = set()
        page = 1
        while True:
            coursesJson = SisApi.requestCoursesFromDep(dep,page)
            if len(coursesJson) == 0:
                break
            for course in coursesJson:
                course_id = int(course['crse_id'])
                if course_id not in course_ids:
                    courses.append({
                            'course_id': course_id,
                            'department': course['subject'],
                            'catalog_number': course['catalog_nbr'],
                            'academic_career_description': course['acad_career_descr'],
                            'credits': course['units'],
                            'description': course['descr']
                        })
                    course_ids.add(course_id)
            page += 1

        return courses
    
    def getCourseExists(dep, catalog_nbr):
        dep = dep.upper()
        courseJson = SisApi.requestCourse(dep, catalog_nbr)
        if(len(courseJson) == 0):
            return False    
        else:
            return True
    
    def getAllCourses():
        depMnemonics = SisApiParser.getDepMnemonics()
        courses = []
        for mnemonic in depMnemonics:
            print(mnemonic)
            courses.extend(SisApiParser.getAllCoursesFromDep(mnemonic))
        return courses