import pandas as pd
from sqlalchemy import create_engine
import requests

from bs4 import BeautifulSoup
import urllib.request
import re

# create the connection string to the MySQL database
engine = create_engine("mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama")
# make the connection to the database
conn = engine.connect()

# Select only the two columns we are intesrested in -> wikiurl and category
sql = """SELECT * FROM ucfnama.sbs_wikipedia where wikiurl != 'none';"""
df = pd.read_sql(sql, engine)

# Wikipedia page
url = 'https://fr.wikipedia.org/wiki/Gustave_Flaubert?action=raw'
page = urllib.request.urlopen(url)
# Open the wikipedia page with soup
soup = BeautifulSoup(page, 'html.parser')

# Split the text in the page
text_page = soup.text.split('\n')
# print(text_page)

# Replace the value that are not necessary
result = list(map(lambda x: x.replace(r'| ',''),text_page))
# find the values we are interested in it! (activités)
find_activity = [i for i in result if i.startswith('activité')]
find_activity

# Append the text page to the dataframe!
text_page_df = pd.DataFrame(text_page,columns={'entities'})
# Clean the | character and append it to the column clean in dataframe!
text_page_df['clean'] = text_page_df.entities.str.replace(r'|','')
text_page_df