import pandas as pd

df = pd.read_csv('output.csv')
courses = df[['ntu_course_code', 'ntu_course_title']].drop_duplicates(subset='ntu_course_code').sort_values(by='ntu_course_code').reset_index(drop=True)
hosts = df[['host_uni']].drop_duplicates(subset='host_uni').sort_values(by='host_uni').reset_index(drop=True)

print(courses)
print(hosts)