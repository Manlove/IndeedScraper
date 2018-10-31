# Import Libraries
import sqlite3 as sq
import requests as urlr
from bs4 import BeautifulSoup as bs

class scraper():
    def __init__(self):
        self.indeed_log = job_log()
        self.url = 'https://www.indeed.com/jobs?q=bioinformatics&sort=date'
        self.getIndeedJobsListPage(self.url)
        self.titles, self.locations, self.companies = self.parseJobsList(self.soup)
        self.log_jobs(self.titles, self.locations, self.companies)

    def getIndeedJobsListPage(self, url):
        page = urlr.get(url)
        self.soup = bs(page.content, 'html.parser')

    def parseJobsList(self, soup):
        titleList = []
        urlList = []
        locationList = []
        companyList = []
        for div in soup.findAll("div", {"class", "result"}):
            a = div.find("a")
            titleList.append(a.get('title'))
            urlList.append('wwww.indeed.com{}'.format(a.get('href')))

            company = div.find("span", {"class", "company"})
            companyList.append(company.getText().strip())

            location = div.find("div", {"class", "location"})
            if location == None:
                location = div.find("span", {"class", "location"})
            locationList.append(location.getText().strip())
        print(urlList)
        return titleList, locationList, companyList

    def log_jobs(self, titles, locations, companies):
        for i in range(0, len(titles)):
            self.indeed_log.insert(titles[i], companies[i], locations[i])

class job_log():
    def __init__(self):
        self.conn = sq.connect('indeed_jobs.db')
        self.curs = self.conn.cursor()
        self.ex = self.curs.execute
        self.setup()

    def setup(self):
        self.ex('CREATE TABLE IF NOT EXISTS jobs (title text, company text, location text, date_applied text)')

    def insert(self, title, company, location, date_applied = None):
        if not date_applied:
            date_applied = ""
        self.ex("INSERT INTO jobs (title, company, location, date_applied) VALUES (?, ?, ?, ?)", (title, company, location, date_applied))

    def reset(self):
        self.ex("DROP TABLE jobs")

indeed = scraper()

a = indeed.indeed_log.ex('SELECT title FROM jobs')
for b in a:
    print(b)
