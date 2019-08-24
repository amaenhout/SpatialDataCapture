import pandas as pd
import geopandas as gpd
import os
from sqlalchemy import create_engine
from shapely.geometry import Point
from shapely.geometry import mapping
import shapely

print('package ready')

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

#SOME STEPS TO ADD THE HEXAGONS ID TO THE SHAPE DATAFRAME !!!
### shape['hex_id'] = ......

# Preparation steps - Create a country list and a category list!
category_list = []
for i in classification['classification']:
    if i not in category_list:
        category_list.append(i)

country_list = []
for i in classification['country']:
    if i not in country_list:
        country_list.append(i)

print('Category_list ready: ' + str(category_list))
print('Country_list ready: ' + str(country_list))

def getCities(country):
    cities = []
    for city in os.listdir('/Volumes/MAENHOUT/hex-city/'+country):
        if(city[0] != "."):
            cities.append(city)
    return cities
### Create Shape and Classification Dataframe for each country.
def groupbycountry(data1,data2,country):
	# if country in country_list:
	country_shape = data1.loc[data1['country']==country]
	country_classification = data2.loc[data2['country']==country]
	country_join = country_classification.merge(country_shape, on=['name','country'])
	country_join = country_join.drop_duplicates()
	print("merge")

	# get a list of the lat lon coordinates
	country_join['coordinates'] = list(zip(country_join.lat,country_join.lon))
	# convert list to point
	country_join.coordinates = country_join.coordinates.apply(Point)
	# converting dataframe to geodataframe 
	gdf_points = gpd.GeoDataFrame(country_join, geometry='coordinates')
	#read polygons for country
	polygons = gpd.read_file('/Volumes/MAENHOUT/hex/'+country+'/'+country+'.json')
	polygons.columns = ["hex","rand","geometry"]
	polygons.loc[:, 'country'] = country
	gdf_points.crs = polygons.crs
	#spatial join both where a points intersects with a polygon
	country_point_join = gpd.sjoin(gdf_points,polygons,op="intersects")
	country_point_join = country_point_join.rename(columns={'country_left':'country','hex':'hexcountry'})
	country_point_join = country_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,9,11]]
	print("country join")

	#read polygons for europe
	polygons = gpd.read_file('/Volumes/MAENHOUT/hex-europe/europe.json')
	polygons.columns = ["hex","rand","geometry"]
	polygons = polygons[["hex","geometry"]]
	# spatial join
	europe_point_join = gpd.sjoin(country_point_join,polygons,op="intersects")
	europe_point_join = europe_point_join.rename(columns={'hex':'hexeurope'})
	europe_point_join = europe_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,12]]
	print ("europe join")
	#read polygons for cities in this country
	cities = getCities(country)
	polygonscities = gpd.GeoDataFrame()
	for city in cities:
		polygons = gpd.read_file('/Volumes/MAENHOUT/hex-city/'+country+'/'+city+'/'+city+'.json')
		polygons.columns = ["hex","rand","geometry"]
		polygons.loc[:, 'city'] = city
		polygonscities = polygonscities.append(polygons) 

	all_join = gpd.sjoin(europe_point_join,polygonscities,op="intersects",how="left")
	all_join = all_join.rename(columns={'hex':'hexcity'})
	all_join = all_join.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,13]]

	print("city join")
	all_join = all_join[["name","country","classification","hexcountry","hexeurope","hexcity"]]
	return all_join


## Example with FRANCE
france = groupbycountry(shape,classification,'france')

## Get country_df for each country!
# country_df = []
# for i in country_list:
#     country_df.append(i+'_df')

# def getcountrydf(country):
#     for df in country_df:
#         df = groupbycountry(shape,classification,country)
#     return df

## Get top 10 street names for each country / each category c!
def gettopstreet(country):

	country_top_df_list = []
	top_hex_list = []

	df_all = groupbycountry(shape,classification,country)
	## create dataframe for each group -> country, hexcountry
	df_country = df_all[["name","country","classification"]]
	df_country['street_name_count'] = df_country.groupby(["name","classification"])['name'].transform('count')

	df_hexcountry = df_all[["name","country","classification","hexcountry"]]
	df_hexcountry['street_name_count_hexcountry'] = df_hexcountry.groupby(["name","classification","hexcountry"])['name'].transform('count')
	
	for i in category_list:
		# Get all the different top 10 street for each category!
		filterdata_category = df_country.loc[df_country['classification']==i]
		#Country
		filterdata_category = filterdata_category.sort_values(['street_name_count'],ascending=False)
		top_10_cat_df = filterdata_category.drop_duplicates('name', keep='first')
		#Keep only the first occurance name of the 10 famous street names!
		top_10_cat_df = top_10_cat_df.head(10)
		# Append each category_df to list result
		country_top_df_list.append(top_10_cat_df)
		# Append Dataframe in the list to one big dataframe!
		result_df = pd.concat(country_top_df_list)


		# Get all the different top 10 street for each category!
		filterdata_category = df_hexcountry.loc[df_country['classification']==i]
		data_use = filterdata_category[['name','classification','hexcountry','street_name_count_hexcountry']]
		# Hex Country
		filterdata_category_hex_id = data_use.sort_values(['hexcountry','street_name_count_hexcountry'],ascending=False)
		top_hex = filterdata_category_hex_id.drop_duplicates(subset=['name','hexcountry'],keep='first')
		#Keep only the first occurance name of the 5 famous street names!
		top_hex = top_hex.groupby('hexcountry').head(5)
		# Append each category_df to list result
		top_hex_list.append(top_hex) 
		# Append Dataframe in the list to one big dataframe!
		top_hex_result = pd.concat(top_hex_list) 
	

	return  top_hex_result

t= gettopstreet("france")
t.hexcountry.unique()
t.sort_values(['hexcountry','classification','street_name_count_hexcountry'],ascending=False).loc[t["street_name_count_hexcountry"] > 1,:]
t.loc[t["street_name_count_hexcountry"] > 1,:]


## Get All The Countries in one big table!
top_list = []

for i in country_list:
        get_top = gettopstreet(i)
        top_list.append(get_top)
        all_results = pd.concat(top_list)





################################################################################################################

def getCountry(country):
    countries = []
    for country in os.listdir('Volumes/MAENHOUT/hexes/hex/'):
        if(country[0] != "."):
            countries.append(country)
    return countries

###   FUNCTION TO READ POLYGONS FOR EACH COUNTRY AND APPEND HEX ID   ###
# -------------------------------------------------------------------  #
def groupbycountry(data1,data2,country):
    # if country in country_list:
    country_shape = shape.loc[shape['country']==country]
    country_classification = classification.loc[classification['country']==country]
    country_join = country_classification.merge(country_shape, on=['name','country'])
    country_join = country_join.drop_duplicates()
    print(" -- MERGE -- ")
    
    # get a list of the lat lon coordinates
    country_join['coordinates'] = list(zip(country_join.lat,country_join.lon))
    # convert list to point
    country_join.coordinates = country_join.coordinates.apply(Point)
    # converting dataframe to geodataframe 
    gdf_points = gpd.GeoDataFrame(country_join, geometry='coordinates')
    
    #read polygons for country
    polygons = gpd.read_file('hexes/hex/'+country+'/'+country+'.json')
    polygons.columns = ["hex","rand","geometry"]
    polygons.loc[:, 'country'] = country
    gdf_points.crs = polygons.crs
    
    #spatial join both where a points intersects with a polygon
    country_point_join = gpd.sjoin(gdf_points,polygons,op="intersects")
    country_point_join = country_point_join.rename(columns={'country_left':'country','hex':'hexcountry'})
    country_point_join = country_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,9,11]]
    print(" -- COUNTRY JOIN -- ")
    
    return country_point_join


###   FUNCTION TO GET TOP STREET FOR EACH COUNTRY, EACH CATEGORY, EACH HEX ID   ###
# ------------------------------------------------------------------------------  #
def GetTopStreet(country):
    
    country_list = []
    hex_list = []

    df_all = groupbycountry(shape,classification,country)

    #Create dataframe for each country, each category, each hexid
    df_hexcountry = df_all[["name","country","classification","hexcountry"]]
    df_hexcountry['street_name_count_hexcountry'] = df_hexcountry.groupby(["name","classification","hexcountry"])['name'].transform('count')
    
    print(str(country) + ' Table Ready!') 
    
    for i in category_list:
        # Get all the different top 5 streets for each category in each hexagons!
        filterdata_category_hex = df_hexcountry.loc[df_hexcountry['classification']==i]
    
        # Hex Country
        filterdata_category_hex_id = filterdata_category_hex.sort_values(['hexcountry','street_name_count_hexcountry'],ascending=False)
        top_hex = filterdata_category_hex_id.drop_duplicates(subset=['name','hexcountry'],keep='first')
        #Keep only the first occurance name of the 5 famous street names!
        top_hex = top_hex.groupby('hexcountry').head(5)
        # Append each category_df to list result
        hex_list.append(top_hex) 
        # Append Dataframe in the list to one big dataframe!
        hex_df = pd.concat(hex_list) 
    
    print('Country Hex Table finish!')
    return result_hex_df


###   FOR LOOP TO GET ALL HEX IN SAME DATAFRAME   ###
# ------------------------------------------------- #
final_europe_list = []

for i in country_list:
    country_df = GetTopStreet(i)
    final_europe_list.append(country_df)
    final_europe_df = pd.concat(final_europe_list)

final_europe_df.head()


###   FUNCTION TO GET TOP STREET FOR EACH COUNTRY, EACH CATEGORY   ###
# ----------------------- COUNTRY AGGREGATE -----------------------  #
# -----------------------------------------------------------------  #
def GetCountriesTop(country):
    
    # Create list to store the Dataframe with top values for Countries, Hexagons
    country_top_df_list = []
    top_hex_list = []
    
    # Create Dataframe for country
    df_country = groupbycountry(shape,classification,country)
    df_country['street_name_count'] = df_country.groupby(["name","classification"])['name'].transform('count')

    # Create dataframe for hexagons!
    df_hexcountry = df_all[["name","country","classification","hexcountry"]]
    df_hexcountry['street_name_count_hexcountry'] = df_hexcountry.groupby(["name","classification","hexcountry"])['name'].transform('count')

   
    for i in category_list:
        # Get all the different top 10 street for each category!
        filterdata_category = df_country.loc[df_country['classification']==i]
        filterdata_category = filterdata_category.sort_values(['street_name_count'],ascending=False)
        #Keep only the first occurance name of the 10 famous street names!
        top_10_cat_df = filterdata_category.drop_duplicates('name', keep='first')
        top_10_cat_df = top_10_cat_df.head(5)
        # Append each category_df to list result
        country_top_df_list.append(top_10_cat_df)
        # Append Dataframe in the list to one big dataframe!
        result_df = pd.concat(country_top_df_list)
        
    return  result_df

all_country = []
for i in country_list:
    all_country.append(GetCountriesTop(i))
    all_country_df = pd.concat(all_country)

all_country_df