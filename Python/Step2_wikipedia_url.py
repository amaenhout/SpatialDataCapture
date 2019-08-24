import requests
import pandas as pd
import wptools
from sqlalchemy import create_engine
import re
import wikipedia
from keys import *
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
pd.options.mode.chained_assignment = None
print("Wikipedia")
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama?charset=utf8mb4')
conn = engine.connect()
print("SQL connected")

def getCountries():
	#search for unique countries
	countries = pd.read_sql("SELECT DISTINCT country FROM sbs_street_names order by country",con = conn)["country"].tolist()
	print("the countries are: "+ str(countries))
	return countries

def getLanguages(country):
	languages = []
	languages = pd.read_sql('SELECT language FROM sbs_countries_streets WHERE country = %(country)s;',con = conn,params={"country":country}).iloc[0][0]
	languages = languages.split(",")
	if 'en' not in languages:
		languages.append('en')
	return languages

def getStreet(country):
	#get all the streets for this country
	datastreets = pd.read_sql_query("SELECT * FROM sbs_street_names WHERE country = %(country)s limit 600",con = conn, params={"country":country})
	print(" data read")
	return datastreets

def getRawUrl(name,language):
	# page = wptools.page(name,silent=True, lang=language).get_query()
	# url_raw = page.data['url_raw']
	# print("yes "+ str(language))
	# return url_raw
	
	wikipedia.set_lang(language)
	page = wikipedia.page(name)
	url_raw = page.url + "?action=raw" 
	return url_raw

def getInfobox(text_page_df):
	#get index infobox
	startindex = list(text_page_df.loc[text_page_df["clean"].str.startswith("{{infobox") == True].index)[0]
	category = text_page_df.iloc[startindex][1].split(" ",1)[1]
	#get end of infobox
	endindex = list(text_page_df.loc[text_page_df["clean"]== "}}" ].index)[0]
	#get infoboxdata
	dataset = text_page_df.iloc[startindex+1:endindex,:].loc[text_page_df["clean"].str.startswith("*")== False]

	dataset['clean'] = dataset.clean.str.replace(r"\s?\s?\s?\s?\s?\s?\s?\s?\s?\s?\s?\s?\s=\s\s?","=")
	dataset['key'] = dataset.clean.str.split("=",1).str[0].str.lstrip()
	dataset['value'] = dataset.clean.str.split("=",1).str[1].str.lstrip()

	info = dataset[dataset['key'].isin(all)][['key','value']].reset_index(drop=True)
	info = info.append({'key' : 'category' , 'value' : category},ignore_index=True)

	return info

def getPersonendaten(text_page_df): 
	#get index infobox
	startindex = list(text_page_df.loc[text_page_df["clean"].str.contains("personendaten") == True].index)[0]
	
	#get end of infobox
	endindex = list(text_page_df.loc[text_page_df["clean"]== "}}" ].index)[-1]
	#get infoboxdata
	dataset = text_page_df.iloc[startindex+1:endindex,:].loc[text_page_df["clean"].str.startswith("*")== False]
	
	dataset['clean'] = dataset.clean.str.replace(r"\s?\s?\s?\s?\s?\s?\s?\s=\s\s?","=")
	dataset['key'] = dataset.clean.str.split("=",1).str[0].str.lstrip()
	dataset['value'] = dataset.clean.str.split("=",1).str[1].str.lstrip()
	
	info = dataset[dataset['key'].isin(all)][['key','value']].reset_index(drop=True)
	
	return info

def getCategory(text_page_df):
	#get index infobox
	startindex = list(text_page_df.loc[text_page_df["clean"].str.contains("{{") == False].index)[0]-1
	checkstart = text_page_df.iloc[startindex+1:startindex+2,1].item()
	if (checkstart.startswith('{{') == False ):
		raise ValueError
	else: 
		category = text_page_df.iloc[startindex][1].replace("{{","")
		#get end of infobox
		endindex = list(text_page_df.loc[text_page_df["clean"]== "}}" ].index)[0]
		#get infoboxdata
		dataset = text_page_df.iloc[startindex+1:endindex,:].loc[text_page_df["clean"].str.startswith("*")== False]
		dataset['clean'] = dataset.clean.str.replace(r"\s?\s?\s?\s?\s?\s?\s?\s?\s?\s=\s\s?","=")
		dataset['key'] = dataset.clean.str.split("=",1).str[0].str.lstrip()
		dataset['value'] = dataset.clean.str.split("=",1).str[1].str.lstrip()
		
		info = dataset[dataset['key'].isin(all)][['key','value']].reset_index(drop=True)
		
		info = info.append({'key' : 'category' , 'value' : category},ignore_index=True)
		return info

def getTaxobox(text_page_df): 
	#get index infobox

	startindex = list(text_page_df.loc[text_page_df["clean"].str.contains("taxobox") == True].index)[0]
	
	#get end of infobox
	endindex = list(text_page_df.loc[text_page_df["clean"]== "}}" ].index)[-1]
	#get infoboxdata
	dataset = text_page_df.iloc[startindex+1:endindex,:].loc[text_page_df["clean"].str.startswith("*")== False]
	
	dataset['clean'] = dataset.clean.str.replace(r"\s?\s?\s?\s?\s?\s?\s=\s\s?","=")
	dataset['key'] = dataset.clean.str.split("=",1).str[0].str.lstrip()
	dataset['value'] = dataset.clean.str.split("=",1).str[1].str.lstrip()
	#print(dataset)
	#print(all)
	info = dataset[dataset['key'].isin(all)][['key','value']].reset_index(drop=True)
	#print(info)
	return info

def getInfoData(info):

	for key in info.key:
		
		if key in born:
			newkey = "born"
			value = info.loc[info['key'] == key,"value"].str.findall(r"[0-9][0-9][0-9][0-9]").str[0]
			info.loc[info['key'] == key,"key"] = newkey
			info.loc[info['key'] == newkey,"value"] = value

		elif key in died:
			newkey = "died"
			value = info.loc[info['key'] == key,"value"].str.findall(r"[0-9][0-9][0-9][0-9]").str[0]
			info.loc[info['key'] == key,"key"] = newkey
			info.loc[info['key'] == newkey,"value"] = value

		elif key in lived:
			valueborn = info.loc[info['key'] == key,"value"].item().split("-")[0]
			valuedied = info.loc[info['key'] == key,"value"].item().split("-")[1]
			try:
				valuedied = int(valuedied)
			except:
				valuedied = ''
			newkey = "born"
			info.loc[info['key'] == key,"key"] = newkey
			info.loc[info['key'] == newkey,"value"] = valueborn
			newkey = "died"
			info = info.append({'key' : newkey , 'value' : valuedied},ignore_index=True)
		elif key in period:
			newkey = "period"
			value = info.loc[info['key'] == key,"value"].str.findall(r"[0-9][0-9][0-9][0-9]").str[-1]
			info.loc[info['key'] == key,"key"] = newkey
			info.loc[info['key'] == newkey,"value"] = value
		elif key in occupation:
			newkey = "category"
			info.loc[info['key'] == key,"key"] = newkey
		elif key in taxobox:
			newkey = "category"
			info.loc[info['key'] == key,"key"] = newkey
	return info

def getURLdata(url):
	page = urllib.request.urlopen(url)
	# Open the wikipedia page with soup
	soup = BeautifulSoup(page, 'html.parser')
	# Split the text in the page
	text_page = soup.text.split('\n')
	# Append the text page to the dataframe!
	text_page_df = pd.DataFrame(text_page,columns={'entities'})
	# Clean the | character and append it to the column clean in dataframe!
	text_page_df['clean'] = text_page_df.entities.str.replace(r'^\s?\|','').str.lower()

	#CHECK CONSTRAINS 
	
	try:
		dataset = getPersonendaten(text_page_df)
		#print("personen")
		end_df = getInfoData(dataset)
	except:
		try:
			dataset = getInfobox(text_page_df)
			#print("info")
			end_df = getInfoData(dataset)
		except:
			try:
				dataset = getTaxobox(text_page_df)
				#print("cat")
				end_df = getInfoData(dataset)			
			except:
				try:
					dataset = getCategory(text_page_df)
					#print("taxo")
					end_df = getInfoData(dataset)	
				except:
					end_df = 0

	return end_df


def getUrlWiki(datastreets):
	for name in datastreets["name"]:
		#print(name)
		index = datastreets[datastreets["name"] == name].index.values.astype(int)
		if (index % 25 == 0):
			print(" "+ str(200 - index) + "left")
		
		for language in languages:
			try:
				urlraw = getRawUrl(name,language)
				#print(urlraw)
				datastreets.loc[datastreets["name"] == name,"wikiurl"] = urlraw
				testurl = getURLdata(urlraw)
				shape = testurl.shape[0]
				#print(testurl)
				if( shape == 0):
					#if return from (infobox) is empty then go to the next language
					continue
				else:
					#if the infobox has data, stop for loop in languages
					break
			except:
				#if somethings goes wrong return 0, go to next language
				shape = 0 
				testurl = 0
				continue

		if (shape == 0):
			#url = "non"
			datastreets = datastreets.loc[datastreets["name"] != name] 


		else:
			#print(testurl)
			for index,row in testurl.iterrows():
				datastreets.loc[datastreets["name"] == name,row["key"]] = row["value"]
	
	cols_df = list(datastreets)
	
	cols_needed = ["category","born","died","period"]
	for column in cols_needed:
		if column not in cols_df:
			datastreets[column] = np.nan

	
	return datastreets

def PushDataToSql(country,datastreets):
	#check if country is already in database
	try:
		checker = conn.execute('select count(*) from sbs_wikipedia where country = %s;',(country)) 
		checkerrow = int(checker.fetchall()[0][0])
		#checker bigger then 0
		if (checkerrow > 0):
			#delete rows of this country
			conn.execute('DELETE from sbs_wikipedia where country = %s;',(country))
	except:
		print(" First time so new names")
	print(" data ready")

	datastreets.to_sql("sbs_wikipedia", con=conn, if_exists='append', index=False)

	print(" data in sql")


succeed = []
failed = []
#loop over every county
for country in getCountries():
	print("-------------- "+ country + " --------------")
	
	languages = getLanguages(country)

	datastreets = getStreet(country)
	
	wikipedia_df = getUrlWiki(datastreets) 
	

	try:
		PushDataToSql(country,wikipedia_df)
		succeed.append(country)
	except:
		print("SOMETHING WENT WRONG IN ->")
		print(country)
		failed.append(country)
		continue

print("succeed for the following countries")
print(succeed)
print("failed for the following countries")
print(failed)