import requests
from pandas.io.json import json_normalize
import pandas as pd 
from sqlalchemy import create_engine
import calendar

engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()

urls = pd.read_sql("select * from ucfnama.sbs_wikipedia where wikiurl != 'none';",con=conn)

for url in urls['wikiurl']:
	#url= 'https://fr.wikipedia.org/wiki/F%C3%A9lix_%C3%89bou%C3%A9?action=raw'

	t = requests.get(url)
	text = t.text

	text.find('Infobox')
	start = text.find('{{Infobox') + 10
	if (start == 9):
		continue
		
	else: 
		newtext = text[start:]
		stop = newtext.find("}}\n\n''")
		info = newtext[:stop]

		categorynum = info.find('|')
	
		category = info[0:categorynum-2]
		info2 = info[categorynum:stop]

		urls.loc[urls['wikiurl']==url,"category"] = category
		test = info2.replace("| ","").replace("  ","").split("\n")

		#get the language out of the url string
		language = url[8:10]
		#get all values of row of this languages -> not as df but as list
		infotranslation =  pd.read_sql("select * from sbs_info where language = %(language)s;",con = conn, params= {'language':language}).drop(['language'],axis=1).iloc[0].tolist()


		translations = pd.read_sql("select * from sbs_info where language = 'en';",con = conn).drop(['language'],axis=1).iloc[0].tolist()

		for line in range(1,len(test)-1):
			workingline = test[line]
			try:
				split = workingline.split("= ")
				if (split[1] != ''):
					# KEYS ----------------------------------------------------------------------------------------
					key = split[0]
					if (key[-1] == " "):
						key = key[:-1]
					if (key[0] == " "):
						key = key[1:]

					if (language != 'en'): 
						# TRANSLATE KEYS

						if key in infotranslation:
							#get the location of this key
							index = infotranslation.index(key)
							#get based on this lication the translations equivalent as translated key
							key = translations[index]
						#add new key to the list
							urls.loc[urls['wikiurl']==url,key] = ""
						else: 
							continue
					else:
						if key in translations:
							urls.loc[urls['wikiurl']==url,key] = ""
						else:
							continue
					
					# VALUES ----------------------------------------------------------------------------------------
					value = split[1]
					# if the last value in key = born or died  
					if (key in ["birth_date",'death_date']):
						if (value.find("}}") > -1):
							value = value.replace("}}","")
							valuesplit = value.split("|")
							day = valuesplit[1]
							month = valuesplit[2]
							year = valuesplit[3]
							value = (str(day) + " "+ str(month) +" "+ str(year))
					
					urls.loc[urls['wikiurl']==url,key] = value
				else:
					continue
			except:
				continue


	# dict = dict(zip(keys,values))
	# data = pd.DataFrame.from_dict(dict,orient='index').T
	# data.to_csv('info_test.csv')
urls.to_sql('sbs_infobox',con=conn, if_exists = 'replace')
	# print(data.head())
	