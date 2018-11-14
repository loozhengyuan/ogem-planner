import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
import credentials as cred

masterlist = []
auth = HttpNtlmAuth(cred.username, cred.password)
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

    # Finds the current and maximum pages
    nav_raw = soup.findAll('p')[6].find('font').text
    nav_trimmed = re.sub(r'\r\n\t', ' ', nav_raw)
    nav_parsed = nav_trimmed.split()
    current_page = nav_parsed[1]
    maximum_page = nav_parsed[3]
    print("Currently scraping page {} of {}".format(current_page, maximum_page))

    # Appending scraped data to table
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
        break

# Export to CSV
df = pd.DataFrame(masterlist, columns=['host_uni',
                                       'ntu_course_code',
                                       'ntu_course_title',
                                       'host_course_code',
                                       'host_course_title',
                                       'sem_last_offered',
                                       'status',
                                       'last_updated',
                                       'validity'])
df.to_csv('output.csv', index=False)