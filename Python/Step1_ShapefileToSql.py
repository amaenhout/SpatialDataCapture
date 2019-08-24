#-----------------------------------------------PACKAGES-----------------------------------------------------------------

import pandas as pd
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
	else:
		roadname = []
		articles = []
	words = []
	
	if len(roadname) > 0:
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

	data = shapefile.dropna(subset=["name"])
	country_utf8 = ["austria","belgium","italy","portugal","spain","switzerland"]
	country_latin = ["france","germany"]

	if (country in country_utf8):
		data.loc[:,["name"]] = data["name"].str.encode('utf-8',).str.decode('utf-8','ignore').astype('str').str.lower()
	
	if (country in country_latin):
		data.loc[:,["name"]] = data["name"].str.encode('latin-1',).str.decode('utf-8','ignore').astype('str').str.lower()

	print(" head ok")
	data = data.reset_index()

	#copy the street name and add the country name	
	data["Streetname"] = data["name"] #(add country name if neccessary)
	
	##### country CONSTRAINTS:
	if (country == "austria"):
		data.name = data.name.str.replace(r'\/\d.*|\/\s\d.*|\;\s.*|\;.*','')
		data.name = data.name.str.replace(r'^\d.|\s\d$|g\d.*','')
		data.name = data.name.str.replace(r'^b\s\d.*|^b\d.*','')
		data.name = data.name.str.replace(r'^\d.*|^a\s\d.*|^a\d\s.*|^a\b kreuz\s\d\d*','')
		data.name = data.name.str.replace(r'fixme.*|^am\s*|^an\sden\s*|^an\sder\s*|^auf\sdem\s*|^auf\sden\s*|^auf\sder\s*|^auf\s*|^beim\s*|^bei\sden\s|^bei\sder\s*','')	
		data.name = data.name.str.replace(r'^zur\s*|^zum\s*|^zu\sden\s*|^zu\sder\s*|^im\s*|^in\sden\s*|^in\sder\s*|^in\s*','')	
		data.name = data.name.str.replace(r'^zufahrt\szu\s.*|^zufhart\shaus\s.*','')
		data.name = data.name.str.replace(r'^block\s.*|^exit\s.*|^wanderweg\s\d.*','')
	
	if (country == "germany"):
		data.name = data.name.str.replace(r'^\(.*|^\".*|^\!.*|^\'.*|^\+.*|^\-.*','')
		data.name = data.name.str.replace(r'^\?.*|^\<.*|^\;.*|^\[.*|^\_.*|^\/.*','')
		data.name = data.name.str.replace(r'^\d.*|^a\s\d.*|^a\d\s.*|^a\b kreuz\s\d\d*','')
		data.name = data.name.str.replace(r'fixme.*|^am\s*|^an\sden\s*|^an\sder\s*|^auf\sdem\s|^auf\sden\s|^auf\sder\s|^auf\s*|^beim\s*|^bei\sden\s|^bei\sder\s*','')	
		data.name = data.name.str.replace(r'^zur\s*|^zum\s*|^zu\sden\s*|^zu\sder\s*|^im\s*|^in\sden\s*|^in\sder\s*|^in\s*','')	
		data.name = data.name.str.replace(r'^strandaufgang\s.*|^passage\s.*|^wanderweg\s\d.*','')

	if (country == "switzerland"):
		data.name = data.name.str.replace(r'\/\s.*','') 
		data.name = data.name.str.replace(r'^\d.*|^a\s\d.*|^a\d\s.*|^ch\.\s|^champ\-','')
		data.name = data.name.str.replace(r'fixme.*|^am\s*|^an\sder\s*|^auf\sdem\s|^auf\sden\s|^auf\sder\s|^auf\s*|^beim\s*|^bei\sder\s*','')	
		data.name = data.name.str.replace(r'^zur\s*|^zum\s*|^zu\sden\s*|^im\s*|^in\sden\s*|^in\sder\s*','')	

	if (country == "france"):
		data.name = data.name.str.replace(r'^\?.*|^\".*|^\(.*|n°\d|n°\d\d*|^vc\s.*|^v.c.\s\d*','')
		data.name = data.name.str.replace(r'^cr\s\d.*|^cr\d.*|d\s\d.*|d-.*|d\d.*|^z.a.\s*|^za\s','')
		data.name = data.name.str.replace(r'^allée\s\d.*|^fix.*|^gr\s.*|^gr\d.*|^vr\d.*','')	
		data.name = data.name.str.replace(r'^improve.|^voie communale n°\d\s*|^voie communale n°\d\d*','')	

	if (country == "belgium"):
		data.name = data.name.str.replace(r'\s-\s.*','')
		data.name = data.name.str.replace(r'nr\.\s.*',' ')
		data.name = data.name.str.replace(r'\snr.\s.*',' ')
		data.name = data.name.str.replace('!! danger!!',' ')
		data.name = data.name.str.replace('"traffic"',' ')
		data.name = data.name.str.replace(r'\(.*',' ')
		data.name = data.name.str.replace(r'\/.*',' ')
		data.name = data.name.str.replace(r'\d.*',' ')
		data.name = data.name.str.replace(r'^\s.*',' ')
		
	if (country == "italy"):
		data.name = data.name.str.replace(r'\(.*|\".*|\?.*|\#.*|\<.*|\>.*','')
		data.name = data.name.str.replace(r'^\d.*|^a\d\s*|^a\d\d\s*|^a\s\d\s*|^al\s','')
		data.name = data.name.str.replace(r'.*\/|.*\/\s','')
		data.name = data.name.str.replace(r'strada statale\s\d\d\d\s*|strada statale\s\d\d\s*|strada statale\s\d\s*','')
		data.name = data.name.str.replace(r'strada regionale\s\d\d\d\s*|strada regionale\s\d\d\s*|strada regionale\s\d\s*','')
		data.name = data.name.str.replace(r'strada provinciale\s\d\d\d\s*|strada provinciale\s\d\d\s*|strada provinciale\s\d\s*','')
		data.name = data.name.str.replace(r'sp\d.*|sp\s\d.*|sp\s*|^s.p.\s*','')
		data.name = data.name.str.replace(r'^ss\s\d.*|^ss\d.*|ss\s*|^s.s.\s*','')
		data.name = data.name.str.replace(r'^sr\s\d.*|^sr\d.*','')
		data.name = data.name.str.replace(r'^f\d*|^f\s\d*','')
			

	if (country == "portugal"):
		data.name = data.name.str.replace(r'EN\s\d.*','')
		data.name = data.name.str.replace(r'EN\d.*','')
		data.name = data.name.str.replace(r'EM\s\d.*','')
		data.name = data.name.str.replace(r'EM\d.*','')
		data.name = data.name.str.replace(r'estrada nacional\s\d.*','')
		data.name = data.name.str.replace(r'estrada regional\s\d.*','') 
	
	if (country == "spain"):
		data.name = data.name.str.replace(r'\(.*|^\".*|^\?.*|^\#.*|^\*.*|^\-.*|^\>.*','') 
		data.name = data.name.str.replace(r'\(|\)*|.*\s;\s|^a-\d\d\d|^a\d\d\d|^a\.\d\d\d','')
		data.name = data.name.str.replace(r'^bp-\d\d\d\d\s|^bs-\d|^bu-\d\d\d|^bu-\d\d|^bu-p-\d\d\d\d','')
		data.name = data.name.str.replace(r'\d\s*|ª\s*|º\s*|^bi-\d\d\d\s|^bi-\d\d\d\d\s|^bi-r\d\s|^bi-r\d\d\s','')
		data.name = data.name.str.replace(r'^ac-\s*|^bu-v-*|^bv-\s*|^c\/\s|^a-\s*','')
		data.name = data.name.str.replace(r'^dsa\s-\sa\s*|^gr\s-\s*|^sa-a\s*','')
		data.name = data.name.str.replace(r'^pr\sm\-.*|^pm\-\d.*|^pr\-m.*|^m\-.*|^lu\-m.*','')
		data.name = data.name.str.replace(r'^\s-\s*|^ctra.\s|\s;','')
		data.name = data.name.str.replace(r'^#fixme\s.*|^rúa\s\”.*','')
		data.name = data.name.str.replace(r'.*\/calle\s|.*\/\scalle\s','')
		data.name = data.name.str.replace(r'.*\/plaza\s|.*\/\splaza\s','')

	

	data = data[data.name != ' ']
	
	#replace all streetwords in the streetname

	for word in allwords:
		#print(word)
		data.loc[:,["name"]] = data["name"].str.replace(word, '')
	
	print(" words replaced")
	data = data[data.name != '']
	#add the length of the street
	data["length"] = data["geometry"].length
	#add the centroid of the street
	data["lat"] = data["geometry"].centroid.x
	data["lon"] = data["geometry"].centroid.y

	data.loc[:,"country"] = country 
	#-----------------------------------------------------------------------------------------
	#--- https://stackoverflow.com/questions/38361336/write-geodataframe-into-sql-database ---
	#-----------------------------------------------------------------------------------------
	
	# Function to generate WKB hex
	# def wkb_hexer(line):
	# 	return line.wkb_hex
	# data['geometry'] = data['geometry'].apply(wkb_hexer)
	data = data[["osm_id","name","Streetname","length","lat","lon","country"]]
	print(" data is ready")
	
	#check if country streets are already in database
	try:
		checker = conn.execute('select count(*) from sbs_shpcountries where country = %s;',(country)) 
		checkerrow = int(checker.fetchall()[0][0])
		#checker bigger then 0
		if (checkerrow > 0):
			#delete rows of this country
			conn.execute('DELETE from sbs_shpcountries where country = %s;',(country))
	except:
		print(" First time so new names") 
	
	data.to_sql("sbs_shpcountries", con=conn, if_exists='append', index=False)
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
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama?charset=utf8mb4')
conn = engine.connect()

print("SQL connected")

#------------------------------------------------LOOP OVER COUNTRIES-----------------------------------------------------------
for country in getcountries('/Volumes/ARTHUR/using'):
	allwords = getallwords(country)
	#------------------------------------------------SHAPEFILE-----------------------------------------------------------------
	data = getshapedata(country)
	#--------------------------------------------------UNIQUE STREETS----------------------------------------------------------------
	getuniquestreets(data,country)
	
	



