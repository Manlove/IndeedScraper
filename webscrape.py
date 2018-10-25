# Import Libraries
import sqlite3 as sq
import requests as urlr
from bs4 import BeautifulSoup as bs

url = 'https://www.indeed.com/jobs?q=bioinformatics&sort=date'
page = urlr.get(url)
soup = bs(page.content, 'html.parser')


titleList = []
locationList = []
companyList = []

for div in soup.findAll("div", {"class", "result"}):
    a = div.find("a")
    titleList.append(a.get('title'))

    company = div.find("span", {"class", "company"})
    companyList.append(company.getText().strip())

    location = div.find("div", {"class", "location"})
    if location == None:
        location = div.find("span", {"class", "location"})
    locationList.append(location.getText().strip())

class job_log():
    def __init__(self):
        self.conn = sq.connect('indeed_jobs.db')
        self.curs = self.conn.cursor()
        self.setup()

    def setup(self):
        self.curs.execute('CREATE TABLE IF NOT EXISTS jobs (title text, company text, location text, date_applied text)')

    def insert(self, title, company, location, date_applied = None):
        if not date_applied:
            date_applied = ""
        self.curs.execute("INSERT INTO jobs (title, company, location, date_applied) VALUES (?, ?, ?, ?)", (title, company, location, date_applied))

log = job_log()
for i in range(0, len(titleList)):
    log.insert(titleList[i], companyList[i], locationList[i])
    
a = log.conn.execute('SELECT title FROM jobs')
for b in a:
    print(b)
