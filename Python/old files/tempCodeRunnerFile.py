#-----------------------------------------------PACKAGES-----------------------------------------------------------------

import pandas as pd
import numpy as np
import geopandas as gpd
from sqlalchemy import create_engine
import os
pd.options.mode.chained_assignment = None

print("packages ready")
#--------------------------------------------------SQL--------------------------------------------------------------------
# Connect with SQL
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()

print("SQL connected")
#-----------------------------------------------VARIABLES-----------------------------------------------------------------
url = '/Volumes/ARTHUR/using'
countries = []
for country in os.listdir(url):
	if(country[0] != "."):
		countries.append(country)

print("The countries are:")
print("  "+ str(countries))

#all the name that a particular language has for a street .....

#------------------------------------------------LOOP OVER COUNTRIES-----------------------------------------------------------
for country in countries:

	language = pd.read_sql('SELECT language FROM sbs_countries_streets WHERE country = %(country)s;',con = conn,params={"country":country}).iloc[0][0]
	# read text road file
	urlroadtext = 'Textfiles/roadnames_'+language+'.txt'
	textroadfile = open(urlroadtext,"r",encoding="utf-8")
	roadname = textroadfile.read().split("\n")
	
	#read article file
	urlarticletext = 'Textfiles/articles_'+language+'.txt'
	textarticlefile = open(urlarticletext,"r",encoding="utf-8")
	articlename = textarticlefile.read().split("\n")
	
	#all articles
	# #make one list
	allwords = []
	for road in roadname:
		for article in articlename:
			text = road + article
			allwords.append(text)
		allwords.append(road)
	#------------------------------------------------SHAPEFILE-----------------------------------------------------------------
	print("------------------ " + country + " ------------------")
	print(" shapefile")
	#reading shapefile
	# 35106067
	# 31678274
	shapefile = gpd.read_file('/Volumes/ARTHUR/using/'+country+'/gis_osm_roads_free_1.shp')
	print(" shapefile loaded")
	#drop empty -> where the name of the street is empty
	#fr wrong: 178732
	
	data = shapefile.dropna(subset=["name"])
	data.loc[:,["name"]] = data["name"].str.encode('latin-1').str.decode('utf-8',"ignore").astype('str')
	
	print(" head ok")
	data = data.reset_index()

	#delete the B" and the " at the and
	#data.loc[:,["name"]] = data["name"].str[2:-1]

	#copy the street name and add the country name	
	data["Streetname"]  = data["name"] #(add country name if neccessary)
	

	#replace all streetwords in the streetname
	for word in allwords:
		data.loc[:,["name"]] = data["name"].str.replace(word, '')
	
	data = data["name"].replace('', np.nan, inplace=True)