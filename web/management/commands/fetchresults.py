import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Fetches the latest bids from OGEM Website'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)
        parser.add_argument('domain', nargs='+', type=str)
        parser.add_argument('matric', nargs='+', type=str)
        parser.add_argument('year', nargs='+', type=str)
        parser.add_argument('sem', nargs='+', type=str)

    def handle(self, *args, **options):
        masterlist = []

        # Authentication Configuration
        # Note: Password is case-sensitive.
        auth_url = 'https://sso.wis.ntu.edu.sg/webexe88/owa/sso.asp'
        auth_data = {
            'PIN': options['password'][0],
            'bOption': 'OK',
            'UserName': options['username'][0],
            'Domain': options['domain'][0],
        }

        # Query Configuration
        # Note: Matric Number has to be in uppercase.
        query_url = 'https://wis.ntu.edu.sg/pls/lms/instep_apply.view_app_stats'
        query_data = {
            'p1': options['matric'][0].upper(),
            'p2': '',
            'g_yr': options['year'][0],
            'g_sem': options['sem'][0],
        }

        # Authentication
        s = requests.Session()
        r = s.post(auth_url, data=auth_data)

        # Checks if authenticated
        if r.status_code != 200:
            raise CommandError('Page returned {status_code}! This could be due to wrong credentials or faulty link.'.format(
                status_code=r.status_code))

        # Query URL
        d = s.get(query_url, params=query_data)

        # Checks if page valid
        if r.status_code != 200:
            raise CommandError('Page returned {status_code}! This could be due to wrong credentials or faulty link.'.format(
                status_code=r.status_code))

        # Parse OGEM Results
        soup = BeautifulSoup(d.text, features='lxml')
        # Omits first element which contain weird content
        for row in soup.find_all("tr")[1:]:
            rowentry = []
            for data in row.find_all("td"):
                rowentry.append(data.text)
            try:
                # Omits row if its header row by checking if last 3 columns have integer type
                t = int(rowentry[-1])
                masterlist.append(rowentry)
            except ValueError:
                self.stdout.write("Omitting row: {}".format(rowentry))
            except:
                raise CommandError('An error has occured!')


