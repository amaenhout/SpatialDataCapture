import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# Connect with SQL
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')


#amount of countries
countries = len(os.listdir('./Countries'))
print("There are: " + str(countries) + " countries")

for country in os.listdir('./Countries'):
	print(country)
	url = os.listdir('./Countries/' + country)
	print("  Total files: " + str(len(url)))
    
	#empty all data for each country
	alldata =  pd.DataFrame()

	# add data for each data file in directory
	for filename in url:
		data = pd.read_csv('./Countries/'+country+'/'+filename)
		alldata = alldata.append(data)
	
	#print if ready with appeding
	print("  data appended")

	# group by streetname and postcode; -> streets are sometime multiple -> housenumbers
	datacountry = alldata.groupby(['STREET','POSTCODE'])['LON','LAT'].mean().reset_index()
	print("  data grouped")

	#MAYBE -> add coords -> lon lat
	
	#print the total streets
	print("  total streets: " + str(datacountry.shape[0]))
	name = "sbs_" + country
	datacountry.to_sql(name,engine,if_exists = "replace")
	print("  data added to sql")
