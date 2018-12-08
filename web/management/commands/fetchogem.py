import re
import requests
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
from django.core.management.base import BaseCommand, CommandError
from web.models import HostUni, HostCourse, NTUCourse, CourseMatch


class Command(BaseCommand):
    help = 'Flushes current data and fetches the latest records from NBS-OGEM site'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)

    def handle(self, *args, **options):
        username = options['username'][0]
        password = options['password'][0]

        masterlist = []
        auth = HttpNtlmAuth(username, password)
        url = 'http://web.nbs.ntu.edu.sg/undergrad/intranet/StdExchange/gem_explorer/Approve_Course.asp'
        headers = {
            'Referer': 'http://web.nbs.ntu.edu.sg/undergrad/intranet/StdExchange/gem_explorer/Approve_Course.asp',
        }
        payload = {
            'validity': '',
            'Status': 'Approved',
            'NTUCourseCode': '',
            'HostUni': '',
            'btnSearch': 'Search',
            'page': '1',
        }

        s = requests.Session()

        while True:
            # Create a new HTTP request with different parameters
            r = s.post(url, auth=auth, headers=headers, params=payload)
            soup = BeautifulSoup(r.text, features='lxml')

            # Checks if page is valid
            if r.status_code != 200:
                raise CommandError('Page returned {status_code}! This could be due to wrong credentials or faulty link.'.format(
                    status_code=r.status_code))
                break

            # Finds the current and maximum pages
            nav_raw = soup.findAll('p')[4].find('font').text
            nav_trimmed = re.sub(r'\r\n\t', ' ', nav_raw)
            nav_parsed = nav_trimmed.split()
            current_page = nav_parsed[1]
            maximum_page = nav_parsed[3]
            self.stdout.write("Currently scraping page {} of {}".format(
                current_page, maximum_page))

            # Appending scraped data to list format
            for table in soup.findAll('table', class_='tablecolor text'):
                for row in table.findAll('tr')[1:]:
                    rowentry = []
                    for data in row.findAll('td'):
                        rowentry.append(data.text)
                    masterlist.append(rowentry)

            # Increasing page param for next loop
            payload['page'] = str(int(current_page) + 1)

            # Breaking loop if at final page
            if current_page == maximum_page:
                self.stdout.write(self.style.SUCCESS("Successfully finished scraping all pages"))
                break

        # Export to Database
        try:
            total_rows = CourseMatch.objects.all().count()
            CourseMatch.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("{total_rows} rows of existing data has been purged".format(total_rows=total_rows)))
            try:
                for entry in masterlist:
                    host_uni, created = HostUni.objects.get_or_create(name=entry[0])
                    ntu_course, created = NTUCourse.objects.get_or_create(code=entry[1], title=entry[2])
                    host_course, created = HostCourse.objects.get_or_create(code=entry[3], title=entry[4])
                    course_match = CourseMatch.objects.create(
                        host_uni=host_uni,
                        ntu_course=ntu_course,
                        host_course=host_course,
                        sem_last_offered=entry[5],
                        status=entry[6],
                        last_updated=entry[7],
                        validity=entry[8],
                    )
                    course_match.save()
                total_rows = CourseMatch.objects.all().count()
                self.stdout.write(self.style.SUCCESS("{total_rows} rows of new data were successfully written to database".format(total_rows=total_rows)))
            except:
                raise CommandError('Failed to write scraped data to database!')
        except:
            raise CommandError('Failed to access database!')
