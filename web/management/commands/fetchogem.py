import re
import requests
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
from django.core.management.base import BaseCommand, CommandError
from web.models import Entries


class Command(BaseCommand):
    help = 'Flushes current data and fetches the latest records from NBS-OGEM site'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)

    def handle(self, *args, **options):
        username = options['username'][0]
        password = options['password'][0]

        dblist = []
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
            r = s.post(url, auth=auth, headers=headers, params=payload)
            soup = BeautifulSoup(r.text, features='lxml')

            # Checks if page is valid
            if r.status_code != 200:
                raise CommandError('Page returned {status_code}! This could be due to wrong credentials or faulty link.'.format(
                    status_code=r.status_code))
                break

            # Finds the current and maximum pages
            nav_raw = soup.findAll('p')[6].find('font').text
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

                    # Format rowentry for database import [DEPRECATED!]
                    dblist.append(Entries(
                        host_uni=rowentry[0],
                        ntu_course_code=rowentry[1],
                        ntu_course_title=rowentry[2],
                        host_course_code=rowentry[3],
                        host_course_title=rowentry[4],
                        sem_last_offered=rowentry[5],
                        status=rowentry[6],
                        last_updated=rowentry[7],
                        validity=rowentry[8],
                    ))

            # Increasing page param for next loop
            payload['page'] = str(int(current_page) + 1)

            # Breaking loop if at final page
            if current_page == maximum_page:
                self.stdout.write(self.style.SUCCESS("Successfully finished scraping all pages"))
                break

        # Export to Database [DEPRECATED!]
        try:
            total_rows = Entries.objects.all().count()
            Entries.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("{total_rows} rows of existing data has been purged".format(total_rows=total_rows)))
            try:
                Entries.objects.bulk_create(dblist)
                total_rows = Entries.objects.all().count()
                self.stdout.write(self.style.SUCCESS("{total_rows} rows of new data were successfully written to database".format(total_rows=total_rows)))
            except:
                raise CommandError('Failed to write scraped data to database!')
        except:
            raise CommandError('Failed to access database!')
        
