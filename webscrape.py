'''
webscrape.py retrieves a list of jobs from the indeed website, retrieves the pages for the individual jobs and then checks the job discription and logs the job into a database if the job has not been logged and meets a set of requirements.
'''
# Import Libraries
for imports in [1]:
    import sqlite3 as sq
    import requests as urlr
    from bs4 import BeautifulSoup as bs
    from re import findall as refindall
class application():
    def __init__(self):
        self.jobDatabase = job_database()
        self.getJobs()
        print("Jobs have been logged")
        self.exit()
    def getJobs(self):
        webscraper = scraper(self.jobDatabase)
        jobsList = webscraper.getJobs()
        for job in jobsList:
            self.jobDatabase.insert( job.getInfo )
        print(len(jobsList))
    def checkJobs(self):
        pass
    def exit(self):
        self.jobDatabase.shutdown()

class scraper():
    '''Retrieves the jobs list from Indeed site and logs the jobs that have not been logged'''
    def __init__(self, database):
        self.database = database
        self.url = 'https://www.indeed.com/jobs?q=bioinformatics&sort=date'  # job site
    def getJobs(self):
        self.jobs = []
        self.getIndeedJobsListPage(self.url)
        self.parseJobsList(self.soup)
        return self.jobs
    def getIndeedJobsListPage(self, url):
        """Takes a url and retrieves the page, opens the page with BeautifulSoup"""
        page = urlr.get(url)
        self.soup = bs(page.content, 'html.parser')
        # Retrieves the Beautiful soup of the indeed jobs list page
    def parseJobsList(self, soup):
        """Takes the soup of a page and creates job_page objects for the jobs in the soup"""
        for div in soup.findAll("div", {"class", "result"}):
            jobID = ""
            a = div.find("a")
            for h2 in div.findAll('h2', {'class', 'jobtitle'}):
                jobID = h2.get('id').split('_')[1]
            if self.database.checkJobLogged(jobID):
                continue
            title = a.get('title')
            url = 'http://wwww.indeed.com{}'.format(a.get('href'))
            company = div.find("span", {"class", "company"})
            company = company.getText().strip()
            location = div.find("div", {"class", "location"})
            if location == None:
                location = div.find("span", {"class", "location"})
            location = location.getText().strip()
            if jobID != "":
                self.jobs.append( job_page(title, company, location, url, jobID) )
        # Creates job objects from the jobs in the job list.
class job_database():
    '''sql database that holds the job information'''
    def __init__(self):
        self.conn = sq.connect('indeed_jobs.db')
        self.curs = self.conn.cursor()
        self.ex = self.curs.execute
        self.setup()
    def setup(self):
        self.ex('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, jobID TEXT UNIQUE, title TEXT, company TEXT, location TEXT, date_applied TEXT)')
        # Creates a sql table in the database if one is not there
    def insert(self, jobInfo):
        try:
            self.ex("INSERT INTO jobs (id, jobID, title, company, location, date_applied) VALUES (?, ?, ?, ?, ?, ?)", jobInfo)
        except:
            print("An Error has occured with {}:{}\n\tFailed to log".format(jobID, title))
        # Inserts a job into the sql database
    def checkJobLogged(self, jobID):
        idCheck = self.ex("SELECT jobID FROM jobs WHERE jobID == ?", (jobID,))
        if idCheck.fetchall() != []:
            return True
        # Checks if a jobID exists, returns True if YES, False if NO
    def reset(self):
        self.ex("DROP TABLE jobs")
        # Drops the sql table, used for troubleshooting
    def shutdown(self):
        self.conn.close()
        # Closes the sql connection, should be run before closing the application
class job_page():
    def __init__(self, title, company, location, url, id):
        self.title, self.company, self.location, self.url, self.id, self.check = title, company, location, url, id, True
        page = urlr.get(self.url)
        self.soup = bs(page.content, 'html.parser')
        self.parseJob(self.soup)
        #self.checkDiscrip()
    def parseJob(self, soup):
        self.discription = ""
        for div in self.soup.findAll("div", class_="jobsearch-JobComponent-description"):
            for p in div.findAll(['p', 'ul']):
                self.discription += " {}".format(p.getText()).upper()
        # Retrieves the job discription from the job page
    def checkDiscrip(self):
        if not (self.checkEd("PhD", self.discription) and not (self.checkEd("BS", self.discription) or self.checkEd("MS", self.discription))):
            if not refindall("python", self.discription):
                print(refindall("PYTHON", self.discription))
        else:
            print("Requires PhD")
        # Checks the job discription for a set of criterion
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
    def getInfo(self):
        return (self.id, self.title, self.company, self.location, "")

indeed = application()
#a = indeed.indeed_log.ex('SELECT title FROM jobs')
# for b in a:
#     print(b)
