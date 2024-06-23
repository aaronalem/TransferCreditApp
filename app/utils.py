from bs4 import BeautifulSoup
import requests

EQUIVALENCY_PAGE = "https://engineering.virginia.edu/current-students/current-undergraduate-students/transferring-uva-engineering/transfer-credit"

def populate_engineering_equivalencies():
    response = request = requests.get(EQUIVALENCY_PAGE)
    state_name = ""
    equivalencies = []
    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.table
        rows = table.find_all('tr')
        rows.pop(0)
        for row in rows:
            entries = row.find_all('td')
            print(entries)
            if len(entries) == 1:
                state_name = entries[0].string
            else:
                foreign_school_name = entries[0].string

                foreign_course_name = entries[1].string.split()
                foreign_course_department = foreign_course_name[0]
                foreign_catalog_number = foreign_course_name[1]
                foreign_course_state = state_name

                foreign_description = entries[2].string
                foreign_credits = int(entries[3].string)
            
                uva_course_name = entries[4].string.split()
                uva_course_department = uva_course_name[0]
                uva_catalog_number = uva_course_name[1]

                uva_credits = int(entries[5].string)

def main():
    populate_engineering_equivalencies()

if __name__ == "__main__":
    main()