'''
webscrape.py retrieves a list of jobs from the indeed website, retrieves the pages for the individual jobs and then checks the job discription and logs the job into a database if the job has not been logged and meets a set of requirements.
'''
# Import Libraries
for imports in [1]:
    import sqlite3 as sq, requests as urlr, tkinter as tk
    from bs4 import BeautifulSoup as bs
    from re import findall as refindall
    from time import localtime
    from tkinter import messagebox
class Application(tk.Frame):
    def __init__(self, master = None):
        self.root = tk.Tk()
        self.root.title("Job Tracker")
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        master = self.root
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.jobDatabase = job_database()
        self.getJobs()
        self.appliedJobs()
        self.checkJobs()
        self.exit()
    def create_widgets(self):
        self.get_jobs_label = tk.Label(self, text = "Get Jobs").grid(row = 1, column = 0, padx = 5, stick = "w")
        self.get_jobs_button = tk.Button(self, text = "Get Jobs", width = 20, command = self.getJobs).grid(row = 1, column = 2)

        self.check_applied_label = tk.Label(self, text = "Number of applied jobs").grid(row = 2, column = 0, padx = 5, stick = "w")
        self.check_applied_button = tk.Button(self, text = "Count Applied", width = 20, command = self.appliedJobs).grid(row = 2, column = 2)

        self.logged_jobs_label = tk.Label(self, text = "Show Jobs").grid(row = 3, column = 0, padx = 5, stick = "w")
        self.logged_jobs_button = tk.Button(self, text = "Show Jobs", width = 20, command = self.checkJobs).grid(row = 3, column = 2)

        self.output = tk.Text(self, width = 50)
        self.output.grid(row = 4, column = 0, columnspan = 6)

    def getJobs(self):
        webscraper = scraper(self.jobDatabase)
        jobsList = webscraper.getJobs()
        for job in jobsList:
            self.jobDatabase.insert( job )
    def checkJobs(self):
        currentTime = localtime()
        currentTime = currentTime.tm_year * 365 + currentTime.tm_yday
        jobs = self.jobDatabase.ex('''SELECT title, url FROM jobs
                                    WHERE date_retrieved >= ?
                                    ORDER BY date_retrieved ASC''', (currentTime - 30,))
        for i in jobs.fetchall():
            print("{}\t{}".format(i[0], i[1]))
    def appliedJobs(self):
        jobs = self.jobDatabase.ex('''SELECT COUNT(title) FROM jobs
                                    WHERE date_applied != ""''')
        print(jobs.fetchone()[0])
    def exit(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.jobDatabase.shutdown()
            self.root.destroy()

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
        currentTime = localtime()
        currentTime = currentTime.tm_year * 365 + currentTime.tm_yday
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
                self.jobs.append( job_page(title, company, location, url, jobID, currentTime) )
        # Creates job objects from the jobs in the job list.
class job_database():
    '''sql database that holds the job information'''
    def __init__(self):
        self.conn = sq.connect('indeed_jobs.db')
        self.curs = self.conn.cursor()
        self.ex = self.curs.execute
        self.setup()
    def setup(self):
        self.ex('CREATE TABLE IF NOT EXISTS jobs (jobID TEXT UNIQUE, title TEXT, company TEXT, location TEXT, url TEXT, date_retrieved INTEGER, date_applied TEXT)')
        # Creates a sql table in the database if one is not there
    def insert(self, job):
        try:
            self.ex("INSERT INTO jobs (jobID, title, company, location, url, date_retrieved, date_applied) VALUES (?, ?, ?, ?, ?, ?, ?)", job.getInfo())
        except:
            items = job.get("id", "title")
            print("An Error has occured with {}:{}\n\tFailed to log".format(items[0], items[1]))
        # Inserts a job into the sql database
    def checkJobLogged(self, jobID):
        idCheck = self.ex("SELECT jobID FROM jobs WHERE jobID == ?", (jobID,))
        return idCheck.fetchall() != []
        # Checks if a jobID exists, returns True if YES, False if NO
    def reset(self):
        self.ex("DROP TABLE jobs")
        # Drops the sql table, used for troubleshooting
    def shutdown(self):
        self.conn.commit()
        self.conn.close()
        # Closes the sql connection, should be run before closing the application
class job_page():
    def __init__(self, title, company, location, url, id, currentTime):
        self.attributes = {"title":title, "company":company, "location":location, "url":url, "id":id, "time":currentTime}
        page = urlr.get(self.attributes["url"])
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
    def get(self, *attributes):
        if len(attributes) < 1:
            raise Exception("""\nJob get command usage:\n\tPassing the following arguments will return the following attributes\n\t- id: Indeed ID\n\t- title: Job Title\n\t- company: Company Name\n\t- location: Job Location\n\t- url: Indeed URL\n\t-time: date when job was retrieved""")
        else:
            argReturn = []
        for arg in attributes:
            argReturn.append(self.attributes[arg.lower()])
        return tuple(argReturn)
    def getInfo(self):
        output = (self.attributes["id"],
        self.attributes["title"],
        self.attributes["company"],
        self.attributes["location"],
        self.attributes["url"],
        self.attributes["time"], "")
        return output

# job = job_page("Job", "Business", "Earth", "http://www.google.com", "12345")
# job.get("wrong arg")
#
# a = job_database()
# a.reset()
indeed = Application()
