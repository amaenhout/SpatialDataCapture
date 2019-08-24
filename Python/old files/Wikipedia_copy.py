import requests
import pandas as pd
import wptools
from sqlalchemy import create_engine
import re
print("Wikipedia")
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()
print("SQL connected")

def getRawUrl(name,language):
	page = wptools.page(name,silent=True, lang=language).get_query()
	url_raw = page.data['url_raw']
	#print("yes "+ str(language))
	return url_raw


def getInfobox(url):

	t = requests.get(url)
	text = t.text

	text.find('Infobox')
	start = text.find('{{Infobox') + 10
	
	if (start == 9):
		#return empty list of necesarry length
		return 0
	else: 
		
		newtext = text[start:]
		
		stop = newtext.find("}}\n\n''")
		info = newtext[:stop]
		
		#print(re.search("(\A<!--).+(-->)", "",info))
		#categorynum = info.find('\n')
		
		# categorynum = info.find('\n')
		if info.find('|') < info.find('\n'):
			categorynum = info.find('\n')
		else:
			categorynum = info.find('|')

		category = info[0:categorynum]

		# if( category[-1] == " " or category[-2] == "}]"):
		#  	category = info[0:categorynum-1]

		
		if( category[-1] == " " or category[-2] == "}]"):
			category = category[:-1]

		keys = []
		values = []
		
		keys.append("category")
		values.append(category.encode('utf-8').lower())

		info2 = info[categorynum:stop]
		test = info2.replace("  ","").split("\n")
		#get the language out of the url string
		language = url[8:10]
		#get all values of row of this languages -> not as df but as list
		infotranslation =  pd.read_sql("select * from sbs_info where language = %(language)s;",con = conn, params= {'language':language}).drop(['language'],axis=1).iloc[0].tolist()
		translations = pd.read_sql("select * from sbs_info where language = 'en';",con = conn).drop(['language'],axis=1).iloc[0].tolist()

		for line in range(1,len(test)-1):
			workingline = test[line]
			if( workingline.find(" = ") > 0):
				split = workingline.split(" = ",1)
			if( workingline.find("= ") > 0):
				split = workingline.split("= ",1)
			if( workingline.find(" =") > 0):
				split = workingline.split(" =",1)
			if( workingline.find("=") > 0):
				split = workingline.split("=",1)

		
			if (len(split) > 1):
				if (split[1] != '' or split[1] != ' '):
					# KEYS ----------------------------------------------------------------------------------------
					if (split[0].find("| ") == -1):
						key = split[0].replace("|","")
					else:
						key = split[0].replace("| ","")
					
					if( key[-1] == " "):
						key = key[:-1]
					if( key[0] == " "):
						key = key[1:]
					if (language != 'en'): 
						# TRANSLATE KEYS
						if key in infotranslation:
							#get the location of this key
							index = infotranslation.index(key)
							#get based on this location the translations equivalent as translated key
							key = translations[index]
							#add new key to the list
							keys.append(key)
						else: 
							continue
					else:
						if key in translations:
							keys.append(key)
						else:
							continue

					
					#VALUES ----------------------------------------------------------------------------------------
					value = split[1]
					if (key in ["birth_date",'death_date']):
						#replace to birth year
						value = next(iter(re.findall("[0-9]{4,7}", value)), None)
						
					values.append(value)
				
				else:
					continue
			else:
				continue
		return dict(zip(keys,values))



#take all countries 
countries = pd.read_sql('SELECT DISTINCT country FROM sbs_names ',con = conn)["country"].tolist()
print("the countries are: "+ str(countries))
#loop over every county
for country in countries:
	print("-------------- "+ country + " --------------")
	#read language for county
	languages = []
	languages.append(pd.read_sql('SELECT language FROM sbs_countries_streets WHERE country = %(country)s;',con = conn,params={"country":country}).iloc[0][0])
	if 'en' not in languages:
		languages.append('en')

	#get all the streets for this country
	datastreets = pd.read_sql_query("SELECT * FROM sbs_names WHERE country = %(country)s ",con = conn, params={"country":country})
	print(" data read")

	#loop over all streetnames for country
	for name in datastreets["name"]:
		
		index = datastreets[datastreets["name"] == name].index.values.astype(int)
		if (index % 25 == 0):
			print(" "+ str(5431 - index))
		
		for language in languages:
			try:
				urlraw = getRawUrl(name,language)
				#print(urlraw)
				datastreets.loc[datastreets["name"] == name,"wikiurl"] = urlraw
				test = getInfobox(urlraw)
				
				if(test == 0):
					continue
				else:
					break
			except:
				test = 0 
				continue
		if (test == 0):
			urlraw = "none"
			datastreets.loc[datastreets["name"] == name,"wikiurl"] = urlraw
			
		else:
			for key, value in test.items():
				datastreets.loc[datastreets["name"] == name,key] = value

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

	datastreets.to_sql("sbs_wikipedia", con=conn, if_exists='replace', index=False)

	print(" data in sql")

