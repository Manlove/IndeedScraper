# Import Libraries
import sqlite3 as sq
import requests as urlr
from bs4 import BeautifulSoup as bs
from re import findall as refindall

class scraper():
    def __init__(self):
        self.jobs = []
        self.indeed_log = job_log()                    #open jobs database
        self.url = 'https://www.indeed.com/jobs?q=bioinformatics&sort=date'  # job site
        self.getIndeedJobsListPage(self.url)           # retrieve the job list page
        self.parseJobsList(self.soup)                  # retrieves the jobs from the list and adds the jobpage objects to the self.jobs list
        # self.logJobs(self.titles, self.locations, self.companies)
        self.indeed_log.shutdown()
    def getIndeedJobsListPage(self, url):
        """Takes a url and retrieves the page, opens the page with BeautifulSoup"""
        page = urlr.get(url)
        self.soup = bs(page.content, 'html.parser')
    def parseJobsList(self, soup):
        """Takes the soup of a page and creates jobpage objects for the jobs in the soup"""
        for div in soup.findAll("div", {"class", "result"}):
            a = div.find("a")
            for h2 in div.findAll('h2', {'class', 'jobtitle'}):
                jobID = h2.get('id').split('_')[1]
            title = a.get('title')
            url = 'http://wwww.indeed.com{}'.format(a.get('href'))
            company = div.find("span", {"class", "company"})
            company = company.getText().strip()
            location = div.find("div", {"class", "location"})
            if location == None:
                location = div.find("span", {"class", "location"})
            location = location.getText().strip()
            job = jobpage(title, company, location, url, jobID)

            if self.indeed_log.checkJobLogged(job.getID()):
                self.jobs.append(job)
    def logJobs(self, titles, locations, companies):
        for i in range(0, len(titles)):
            self.indeed_log.insert(titles[i], companies[i], locations[i])

class job_log():
    def __init__(self):
        self.conn = sq.connect('indeed_jobs.db')
        self.curs = self.conn.cursor()
        self.ex = self.curs.execute
        self.setup()
    def setup(self):
        self.ex('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, date_applied text)')
    def insert(self, title, company, location, date_applied = None):
        if not date_applied:
            date_applied = ""
        self.ex("INSERT INTO jobs (id, title, company, location, date_applied) VALUES (?, ?, ?, ?, ?)", (title, company, location, date_applied))
    def checkJobLogged(self, job_id):
        print(self.ex("SELECT id FROM jobs WHERE id == ?", job_id))
    def reset(self):
        self.ex("DROP TABLE jobs")
    def shutdown(self):
        self.conn.close()

class jobpage():
    def __init__(self, title, company, location, url, id):
        self.title, self.company, self.location, self.url, self.id, self.check = title, company, location, url, id, True
        page = urlr.get(self.url)
        self.soup = bs(page.content, 'html.parser')
        self.parseJob(self.soup)
        self.checkDiscrip()
    def parseJob(self, soup):
        self.discription = ""
        for div in self.soup.findAll("div", class_="jobsearch-JobComponent-description"):
            for p in div.findAll(['p', 'ul']):
                self.discription += " {}".format(p.getText()).upper()
    def checkDiscrip(self):
        if not (self.checkEd("PhD", self.discription) and not (self.checkEd("BS", self.discription) or self.checkEd("MS", self.discription))):
            if not refindall("python", self.discription):
                print(refindall("PYTHON", self.discription))
        else:
            print("Requires PhD")
    def checkEd(self, position, string):
        strStrt = "[\s\r\n\\/]"
        bach = "BACHELOR'?S?"
        bs = "B\.?S\.?"
        mast = "MASTER'?S?"
        ms = "M\.?S\.?"
        phd = "P\.?H\.?D\.?"
        doct = "DOCTORATE"
        if position == "BS":
            regex = "{}{}|{}{}|^{}|^{}".format(strStrt, bach, strStrt, bs, bach, bs)
        elif position == "MS":
            regex = "{}{}|{}{}|{}GRADUATE|^{}|^{}|^GRADUATE".format(strStrt, mast, strStrt, ms, strStrt, mast, ms)
        elif position == "PhD":
            regex = "{}{}|{}{}|^{}|^{}".format(strStrt, doct, strStrt, phd, doct, phd)
        return refindall(regex, string.upper())
    def getID(self):
        return self.id

indeed = scraper()
#a = indeed.indeed_log.ex('SELECT title FROM jobs')
# for b in a:
#     print(b)
