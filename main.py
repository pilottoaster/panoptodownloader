import requests
import xmltodict
import sqlite3
import os
from dotenv import load_dotenv
from todatabase import ToDatabase
from downloader import download_file

# Loads the .env file
load_dotenv()

base64ApiKey = os.getenv('BASE64APIKEY')
oauthUrl = os.getenv('OAUTHURL')
xmlurl = os.getenv('XMLURL')

# Creates on disk database to keep track of what's been downloaded
con = sqlite3.connect('panopto.db')

# Creates db cursor
cur = con.cursor()

# Creates the database "videos" if it does not exist
try:
    cur.execute('CREATE TABLE videos(classn,folderid,url,title,downloaded)')
except sqlite3.OperationalError as err:
    if err == 'table videos already exists':
        print('Table already created, continuing...')

# Opens a session to maintain session token for the rest of the query's
session = requests.session()
# Gets session token
r = session.get(oauthUrl + base64ApiKey)

# Asks for input on the class ID to make sure we can run this dynamically to download what we need
classID = input('Please paste your courseID: \n')

# Gets list of all recordings available for inputted classID
course_xml_data = session.get(xmlurl + classID + '&type=mp4')

# Parses the response to a dictionary so that the information can be accessed easily
data = xmltodict.parse(course_xml_data.content)

# Iterates through all the data for that class and pushes it to the database if it does not exist
for item in data['rss']['channel']['item']:
    ToDatabase(data['rss']['channel']['title'], item['title'], classID, item['guid'])

    # Calls the downloader function to handle the logic of downloading the files
    download_file(item['title'], item['guid'])

