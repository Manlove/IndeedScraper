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

   
db = sq.connect('indeed_jobs.db')
#db.execute('CREATE TABLE IF NOT EXISTS jobs (title text, company text, location text, date_applied text)')
db.execute('DROP TABLE IF EXISTS jobs')
db.execute('CREATE TABLE jobs (title text, company text, location text)')


for i in range(0, len(titleList)):
    insert = (titleList[i], companyList[i], locationList[i])
    db.execute("INSERT INTO jobs (title,company,location) VALUES (?, ?, ?)", insert)

    
db.commit()
a = db.execute('SELECT title FROM jobs')
for b in a:
    print(b)
    

