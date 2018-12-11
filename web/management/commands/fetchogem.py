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

            # Finds the current and maximum pages
            try:
                nav_raw = soup.findAll('p')[4].find('font').text
                nav_trimmed = re.sub(r'\r\n\t', ' ', nav_raw)
                nav_parsed = nav_trimmed.split()
                current_page = nav_parsed[1]
                maximum_page = nav_parsed[3]
                self.stdout.write("Currently scraping page {} of {}".format(
                    current_page, maximum_page))
            except:
                raise CommandError('Failed to derive to correct pagination when crawling!')

            # Appending scraped data to list format
            try:
                for table in soup.findAll('table', class_='tablecolor text'):
                    for row in table.findAll('tr')[1:]:
                        rowentry = []
                        for data in row.findAll('td'):
                            rowentry.append(data.text)
                        masterlist.append(rowentry)
            except:
                raise CommandError('Failed to derive data entries when crawling!')

            # Increasing page param for next loop
            payload['page'] = str(int(current_page) + 1)

            # Breaking loop if at final page
            if current_page == maximum_page:
                self.stdout.write(self.style.SUCCESS("Successfully finished scraping all pages."))
                break

        # Export to Database
        if len(masterlist) > 1000 and len(masterlist) < 5000:
            self.stdout.write(self.style.SUCCESS("Verified that scrapped entries are within probable range of 1000-5000 rows."))
            try:
                total_rows = CourseMatch.objects.all().count()
                CourseMatch.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("{total_rows} rows of existing data has been purged".format(total_rows=total_rows)))
                try:
                    for entry in masterlist:
                        
                        # Get or create HostUni entry
                        try:
                            host_uni, created = HostUni.objects.get_or_create(name=entry[0])
                        except:
                            raise CommandError('Failed to get or create HostUni entry!')
                        
                        # Get or create NTUCourse entry
                        try:
                            ntu_course = NTUCourse.objects.get(code=entry[1])
                        except NTUCourse.MultipleObjectsReturned:
                            self.stdout.write(self.style.WARNING("Multiple objects were detected for {code}. Associating with latest entry.".format(code=entry[1])))
                            ntu_course = NTUCourse.objects.filter(code=entry[1]).last()
                        except NTUCourse.DoesNotExist:
                            self.stdout.write("{code} not found in database. Creating a new entry for {code}.".format(code=entry[1]))
                            ntu_course = NTUCourse.objects.create(code=entry[1], title=entry[2])
                        except:
                            raise CommandError('Failed to get or create NTUCourse entry!')
                        
                        # Get or create HostCourse entry
                        try:
                            host_course = HostCourse.objects.get(code=entry[3])
                        except HostCourse.MultipleObjectsReturned:
                            self.stdout.write(self.style.WARNING("Multiple objects were detected for {code}. Associating with latest entry.".format(code=entry[3])))
                            host_course = HostCourse.objects.filter(code=entry[3]).last()
                        except HostCourse.DoesNotExist:
                            self.stdout.write("{code} not found in database. Creating a new entry for {code}.".format(code=entry[3]))
                            host_course = HostCourse.objects.create(code=entry[3], title=entry[4])
                        except:
                            raise CommandError('Failed to get or create HostCourse entry!')
                        
                        # Create CourseMatch entries
                        try:
                            course_match = CourseMatch.objects.create(
                                host_uni=host_uni,
                                ntu_course=ntu_course,
                                host_course=host_course,
                                sem_last_offered=entry[5],
                                status=entry[6],
                                last_updated=entry[7],
                                validity=entry[8],
                            )
                        except:
                            raise CommandError('Failed to create CourseMatch entry!')
                    
                    total_rows = CourseMatch.objects.all().count()
                    self.stdout.write(self.style.SUCCESS("{total_rows} rows of new data were successfully written to database".format(total_rows=total_rows)))
                except:
                    raise CommandError('Failed to write scraped data to database!')
            except:
                raise CommandError('Failed to access database!')
        else:
            raise CommandError('Scrapped entries is NOT in probable range of 1000-5000 rows. No database changes made.')
