import geopandas as gpd
import os
import pandas as pd
from shapely.geometry import Point
from shapely.geometry import mapping
from sqlalchemy import create_engine
import shapely

print("step4 - HEX")

#connect with SQL database
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama?charset=utf8mb4')
conn = engine.connect()
print("SQL connected")

# get all the street points where there is a classification
shape = pd.read_sql("SELECT DISTINCT shp.name,shp.Streetname,shp.country,shp.length,shp.lat,shp.lon FROM ucfnama.sbs_shpcountries shp;",con = conn)
print("shapes loaded")
print(shape["country"].unique())

classification  = pd.read_sql("SELECT c.name,c.country,c.classification,c.sub_class,c.period_class FROM ucfnama.sbs_classification c;",con = conn)
print("classification loaded")
print(classification["country"].unique())

classification = classification.drop_duplicates(subset=["name","country"], keep='first')
points = pd.merge(shape,classification, on=["name","country"])

points.head()
# get a list of the lat lon coordinates
points['coordinates'] = list(zip(points.lat,points.lon))

# convert list to point
points.coordinates = points.coordinates.apply(Point)
# converting dataframe to geodataframe 
gdf_points = gpd.GeoDataFrame(points, geometry='coordinates')

def getcountries(url):
	countries = []
	for country in os.listdir(url):
		if(country[0] != "."):
			countries.append(country)
	return countries
# ------------------------ SPATIAL JOIN FOR COUNTRY ID ------------------------
#empty all countries geodataframe
allcountries = gpd.GeoDataFrame()
listcountries = list()
for country in getcountries('/Volumes/MAENHOUT/hex'):
	polygons = gpd.read_file('/Volumes/MAENHOUT/hex/'+country+'/'+country+'.json')
	polygons.columns = ["hex","rand","geometry"]
	polygons.loc[:, 'country'] = country
	allcountries = allcountries.append(polygons) 
	print(country)
	listcountries.append(country)

#set crs of points and allcountries equal
gdf_points.crs = allcountries.crs
#spatial join both where a points intersects with a 
join_countries = gpd.sjoin(gdf_points,allcountries,op="intersects")
join_countries = join_countries.rename(columns={'country_left':'country','hex':'hexcountry'})
join_countries.head()
datacountry = join_countries.iloc[:,[0,1,2,3,4,5,6,7,8,9,11]]
# ------------------------ SPATIAL JOIN FOR EUROPE ID ------------------------
#Europe
europe = gpd.read_file('/Volumes/MAENHOUT/hex-europe/europe.json')
europe.columns = ["hex","rand","geometry"]
europe = europe[["hex","geometry"]]

gdf_points.crs = europe.crs
# spatial join
joineurope = gpd.sjoin(datacountry,europe,op="intersects")
joineurope = joineurope.rename(columns={'hex':'hexeurope'})
dataeurope = joineurope.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,12]]

# ------------------------ SPATIAL JOIN FOR CITY ID ------------------------
allcities = gpd.GeoDataFrame()
listcities = []
for country in listcountries:
	try:
		for city in getcountries('/Volumes/MAENHOUT/hex-city/'+country):
			polygons = gpd.read_file('/Volumes/MAENHOUT/hex-city/'+country+'/'+city+'/'+city+'.json')
			polygons.columns = ["hex","rand","geometry"]
			polygons.loc[:, 'city'] = city
			allcities = allcities.append(polygons) 
			listcities.append(city)
	except:
		next


gdf_points.crs = allcities.crs

joincities = gpd.sjoin(dataeurope,allcities,op="intersects",how="left")
joincities = joincities.rename(columns={'hex':'hexcity'})

data = joincities.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,13,15]]
data = data.fillna(value="unclassified")

# --------- COUNTRIES
# COUNTRY CLASSIFICATION SUB_CLASS PERIOD HEXCOUNTRY

countries_df = data.loc[:,["name","hexcountry","country","classification","sub_class","period_class"]]

groupby_class = countries_df.groupby(["hexcountry","classification","country"],as_index=False).count().iloc[:,:4]
pivot_class = groupby_class.pivot_table(index=['hexcountry','country'], columns='classification', values='name').reset_index()

groupby_sub_class = countries_df.groupby(["hexcountry","sub_class","country"],as_index=False).count().iloc[:,:4]
pivot_sub_class = groupby_sub_class.pivot_table(index=['hexcountry','country'], columns='sub_class', values='name').reset_index()
pivot_sub_class = pivot_sub_class.rename(columns={'other':'other_sub'})
pivot_sub_class = pivot_sub_class.drop(columns="country")
print("before group")
groupby_period_class = countries_df.groupby(["hexcountry","period_class","country"],as_index=False).count().iloc[:,:4]
pivot_period_class = groupby_period_class.pivot_table(index=['hexcountry','country'], columns='period_class', values='name').reset_index()
pivot_period_class = pivot_period_class.rename(columns={'other':'other_period'})
pivot_period_class = pivot_period_class.drop(columns="country")

hexcountries = pd.merge(pd.merge(pivot_class,pivot_sub_class,on="hexcountry"),pivot_period_class, on="hexcountry")

hexcountries = hexcountries.rename(columns={'hexcountry':'hex'})

hexcountries.to_sql("sbs_hexcountries", con=conn, if_exists='replace', index=False)

print("hex countries in sql")



# EU
europe_df = data.loc[:,["name","hexeurope","classification","sub_class","period_class"]]

groupby_class = europe_df.groupby(["hexeurope","classification"],as_index=False).count().iloc[:,:4]
pivot_class = groupby_class.pivot_table(index=['hexeurope'], columns='classification', values='name').reset_index()

groupby_sub_class = europe_df.groupby(["hexeurope","sub_class"],as_index=False).count().iloc[:,:4]
pivot_sub_class = groupby_sub_class.pivot_table(index=['hexeurope'], columns='sub_class', values='name').reset_index()
pivot_sub_class = pivot_sub_class.rename(columns={'other':'other_sub'})

print("before group")
groupby_period_class = europe_df.groupby(["hexeurope","period_class"],as_index=False).count().iloc[:,:4]
pivot_period_class = groupby_period_class.pivot_table(index=['hexeurope'], columns='period_class', values='name').reset_index()
pivot_period_class = pivot_period_class.rename(columns={'other':'other_period'})

hexeurope = pd.merge(pd.merge(pivot_class,pivot_sub_class,on="hexeurope"),pivot_period_class, on="hexeurope")

hexeurope = hexeurope.rename(columns={'hexeurope':'hex'})
hexeurope.to_sql("sbs_hexeurope", con=conn, if_exists='replace', index=False)
print("hex eu in sql")

# ---------- CITY
city_df = data.loc[:,["name","hexcity","city","classification","sub_class","period_class"]]

groupby_class = city_df.groupby(["hexcity","classification","city"],as_index=False).count().iloc[:,:4]
pivot_class = groupby_class.pivot_table(index=['hexcity','city'], columns='classification', values='name').reset_index()

groupby_sub_class = city_df.groupby(["hexcity","sub_class",'city'],as_index=False).count().iloc[:,:4]
pivot_sub_class = groupby_sub_class.pivot_table(index=['hexcity','city'], columns='sub_class', values='name').reset_index()
pivot_sub_class = pivot_sub_class.rename(columns={'other':'other_sub'})
pivot_sub_class = pivot_sub_class.drop(columns="city")

print("before group")
groupby_period_class = city_df.groupby(["hexcity","period_class",'city'],as_index=False).count().iloc[:,:4]
pivot_period_class = groupby_period_class.pivot_table(index=['hexcity','city'], columns='period_class', values='name').reset_index()
pivot_period_class = pivot_period_class.rename(columns={'other':'other_period'})
pivot_period_class = pivot_period_class.drop(columns="city")

hexcity = pd.merge(pd.merge(pivot_class,pivot_sub_class,on="hexcity"),pivot_period_class, on="hexcity")

hexcity = hexcity.rename(columns={'hexcity':'hex'})

hexcity.to_sql("sbs_hexcity", con=conn, if_exists='replace', index=False)
print("hex city in sql")

