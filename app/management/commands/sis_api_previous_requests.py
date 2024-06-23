import requests

class SisApiPreviousSemester:
    baseURL = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"

    def requestDepMnemonics():
        while True:
            try:
                r = requests.get("https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1228")
                return r.json()
            except requests.exceptions.ConnectTimeout:
                print("Timed out, trying again...")
    
    def requestCoursesFromDep(dep, page):
         while True:
            try:
                r = requests.get(SisApiPreviousSemester.baseURL + "&term=1228&subject={}&page={}".format(dep, page))
                return r.json()
            except requests.exceptions.ConnectTimeout:
                print("Timed out, trying again...")
    
    def requestCourse(dep, catalog_nbr):
         while True:
            try:
                r = requests.get(SisApiPreviousSemester.baseURL + "&term=1228&subject={}&catalog_nbr={}".format(dep, catalog_nbr))
                return r.json()
            except requests.exceptions.ConnectTimeout:
                print("Timed out, trying again...")