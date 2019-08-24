#-----------------------------------------------PACKAGES-----------------------------------------------------------------

import pandas as pd
import numpy as np
import geopandas as gpd
from sqlalchemy import create_engine
import os
pd.options.mode.chained_assignment = None

print("packages ready")

#-----------------------------------------------FUNCTIONS-----------------------------------------------------------------
def getcountries(url):
	countries = []
	for country in os.listdir(url):
		if(country[0] != "."):
			countries.append(country)

	print("The countries are:")
	print("  "+ str(countries))
	return countries

def replace_words(language):
	if (language == "en"): 
		from roadnames import en as roadname
		from articles import en as articlename
	elif (language == "fr"):
		from roadnames import fr as roadname
		from articles import fr as articlename
	elif (language == "de"):
		from roadnames import de as roadname
		from articles import de as articlename
	elif (language == "nl"):
		from roadnames import nl as roadname
		from articles import nl as articlename
	elif (language == "es"):
		from roadnames import es as roadname
		from articles import es as articlename
	elif (language == "pt"):
		from roadnames import pt as roadname
		from articles import pt as articlename
	elif (language == "it"):
		from roadnames import it as roadname
		from articles import it as articlename

	words = []
	for road in roadname:
		if (articlename == [""]):
			words.append(road)
		else:
			for article in articlename:
				text = road + article
				words.append(text)
			words.append(road)
	
	
	return words

def getallwords(country):
	language = pd.read_sql('SELECT language FROM sbs_countries_streets WHERE country = %(country)s;',con = conn,params={"country":country}).iloc[0][0]
	allwords = []
	if (len(language) > 2):
		languages = language.split(",")
		for l in languages:
			allwords = allwords + (replace_words(l))
	else:
		#loop over languages 
		allwords = replace_words(language)
	
	return allwords

def getshapedata(country):
	print("------------------ " + country + " ------------------")
	print(" shapefile")
	#reading shapefile
	# 35106067
	# 31678274
	shapefile = gpd.read_file('/Volumes/ARTHUR/using/'+country+'/gis_osm_roads_free_1.shp')
	print(" shapefile loaded")
	#drop empty -> where the name of the street is empty
	#fr wrong: 178732
	
	# add info
	streets = shapefile.shape[0]
	conn.execute('UPDATE sbs_countries_streets SET streets = %s WHERE country = %s;',(streets, country)) 

	data = shapefile.dropna(subset=["name"]).head(10000)

	data.loc[:,["name"]] = data["name"].str.encode('latin-1','ignore').str.decode('utf-8').astype('str').str.lower()

	print(" head ok")
	data = data.reset_index()

	#copy the street name and add the country name	
	data["Streetname"]  = data["name"] #(add country name if neccessary)
	
	##### country CONSTRAINTS:
	if (country == "belgium"):
		data.name = data.name.str.replace(r'\s-\s.*','')
		data.name = data.name.str.replace(r'nr.\s.*',' ')
		data.name = data.name.str.replace(r'\snr.\s.*',' ')
		data.name = data.name.str.replace('!! danger!!',' ')
		data.name = data.name.str.replace('"traffic"',' ')
		data.name = data.name.str.replace(r'\(.*',' ')
		data.name = data.name.str.replace(r'\/.*',' ')
		data.name = data.name.str.replace(r'\d.*',' ')
		data.name = data.name.str.replace(r'^\s.*',' ')
		
	if (country == "italy"):
		data.name = data.name.str.replace(r'^sp\s\d$|^sp\s\d\d$|^sp\s\d\d\d$|^sp\d$|^sp\d\d$|^sp\d\d\d$',' ')
		data.name = data.name.str.replace(r'^ss\s\d|^ss\d$|^ss\d\d$|^ss\d\d\d$',' ')
		data.name = data.name.str.replace(r'^a\d|^a\d\d|^a\s',' ')
		data.name = data.name.str.replace(r'^c.a.i',' ')
		data.name = data.name.str.replace(r'^null|^fixme bike|^fixme - bike|^fixme\s\d|^fixme!!!|^fixme -bike|^ls\d',' ')
		data.name = data.name.str.replace(r'^\s\s\d|^\s\d$|^\s\d\d;|^\s\d\d dir',' ')
		data.name = data.name.str.replace(r'strada statale \d\d$|^strada statale \d\d\d$',' ')	
		data.name = data.name.str.replace(r'^sp\d.*',' ')
		data.name = data.name.str.replace(r'^ss\d.*',' ')
		data.name = data.name.str.replace(r'^sr\d.*',' ')
		data.name = data.name.str.replace(r'\d.*"',' ')

	
	data = data[data.name != ' ']
	
	#replace all streetwords in the streetname

	for word in allwords:
		print(word)
		data.loc[:,["name"]] = data["name"].str.replace(word, '')
	
	print(" words replaced")
	data = data[data.name != '']
	
	#add the length of the street
	data["length"] = data["geometry"].length
	
	#add the centroid of the street
	data["lat"] = data["geometry"].centroid.x
	data["lon"] = data["geometry"].centroid.y

	#-----------------------------------------------------------------------------------------
	#--- https://stackoverflow.com/questions/38361336/write-geodataframe-into-sql-database ---
	#-----------------------------------------------------------------------------------------
	
	# Function to generate WKB hex
	def wkb_hexer(line):
		return line.wkb_hex
	data['geometry'] = data['geometry'].apply(wkb_hexer)
	
	print(" data is ready")
	#add data to SQL Workbench
	name = "sbs_" + country
	data.to_sql(name, con=conn, if_exists='replace', index=False)

	print(" data in SQL ")
	
	streetsdrop = data.shape[0]
	conn.execute('UPDATE sbs_countries_streets SET streetsdrop = %s WHERE country = %s;',(streetsdrop, country)) 

	return data

def getuniquestreets(data,country):
	#get the unique street names
	streetnames = data["name"].unique()

	#create dataframe from name -> unique id's
	datastreets = pd.DataFrame({'name':streetnames})
	datastreets["country"] = country
	
	#check if country is already in database
	try:
		checker = conn.execute('select count(*) from sbs_street_names where country = %s;',(country)) 
		checkerrow = int(checker.fetchall()[0][0])
		#checker bigger then 0
		if (checkerrow > 0):
			#delete rows of this country
			conn.execute('DELETE from sbs_street_names where country = %s;',(country))
	except:
		print(" First time so new names") 
	
	datastreets.to_sql("sbs_street_names", con=conn, if_exists='append', index=False)

	unique = streetnames.shape[0]
	conn.execute('UPDATE sbs_countries_streets SET streetsunique = %s WHERE country = %s;',(unique, country)) 
	print(" unique streets in sql")
#--------------------------------------------------SQL--------------------------------------------------------------------
# Connect with SQL
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()

print("SQL connected")
#-----------------------------------------------VARIABLES-----------------------------------------------------------------


countries = getcountries('/Volumes/ARTHUR/using')

#all the name that a particular language has for a street .....

#------------------------------------------------LOOP OVER COUNTRIES-----------------------------------------------------------
for country in countries:
	
	allwords = getallwords(country)
	#------------------------------------------------SHAPEFILE-----------------------------------------------------------------
	data = getshapedata(country)
	#--------------------------------------------------UNIQUE STREETS----------------------------------------------------------------
	getuniquestreets(data,country)
	
	



