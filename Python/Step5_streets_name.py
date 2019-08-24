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

wikipedia  = pd.read_sql("SELECT w.name,w.country,w.wikiurl,w.category FROM ucfnama.sbs_wikipedia w;",con = conn)
print('wikipedia loaded')

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

################################################################################################################

def getCities(country):
    cities = []
    for city in os.listdir('hexes/hex-city/'+country):
        if(city[0] != "."):
            cities.append(city)
    return cities

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
    
    hex_list = []

    df_all = groupbycountry(shape,classification,country)

    #Create dataframe for each country, each category, each hexid
    df_hexcountry = df_all[["name","country","classification",'hexeurope',"sub_class","period_class"]]
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
    return hex_df


###   FOR LOOP TO GET ALL HEX IN SAME DATAFRAME   ###
# ------------------------------------------------- #
hex_country_list = []
for i in country_list:
    country_df = GetTopStreet(i)
    hex_country_list.append(country_df)
    top_hex_country = pd.concat(hex_country_list)
    top_hex_country = top_hex_country.rename(columns={'hexcountry':'hex','street_name_count_hexcountry':'street_name_count'})
    top_hex_country = top_hex_country.reset_index()
    top_hex_country = top_hex_country.drop(columns='index')

print('Dataframe for top streets in Countries for each categories Ready')
print('Data Push to SQL')
top_hex_country.to_sql("sbs_hex_streets", con=conn, if_exists='replace', index=False)
print("hex city in sql")

################################################################################################################


###   FUNCTION TO READ POLYGONS FOR EACH COUNTRY AND APPEND EUROPE HEX ID   ###
# --------------------------------------------------------------------------  #
# Read Polygons for each country!
def Europe(data1,data2,country):
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
    
    #read polygons for europe
    polygons = gpd.read_file('hexes/hex-europe/europe.json')
    polygons.columns = ["hex","rand","geometry"]
    polygons = polygons[["hex","geometry"]]
    gdf_points.crs = polygons.crs
    
    # spatial join
    europe_point_join = gpd.sjoin(gdf_points,polygons,op="intersects")
    europe_point_join = europe_point_join.rename(columns={'hex':'hexeurope'})
    europe_point_join = europe_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,9,11]]
    print (" -- EUROPE JOIN -- ")

    return europe_point_join


###   FUNCTION TO READ POLYGONS FOR EACH COUNTRY AND APPEND EUROPE HEX ID   ###
# --------------------------------------------------------------------------  #
def GetTopEurope(country):
    
    europe_list = []

    df_all = Europe(shape,classification,country)

    #Create dataframe for each country, each category, each hexid
    df_hexeurope = df_all[["name","country","classification",'hexeurope',"sub_class","period_class"]]
    df_hexeurope['street_name_count_hexeurope'] = df_hexeurope.groupby(["name","classification","hexeurope"])['name'].transform('count')
    
    print(str(country) + ' dataframe ready') 
    
    for i in category_list:
        # Get all the different top 5 streets for each category in each hexagons!
        filterdata_category_hex = df_hexeurope.loc[df_hexeurope['classification']==i]
    
        # Hex Europe
        filterdata_category_hex_id = filterdata_category_hex.sort_values(['hexeurope','street_name_count_hexeurope'],ascending=False)
        top_hex = filterdata_category_hex_id.drop_duplicates(subset=['name','hexeurope'],keep='first')
        #Keep only the first occurance name of the 5 famous street names!
        top_hex = top_hex.groupby('hexeurope').head(5)
        # Append each category_df to list result
        europe_list.append(top_hex) 
        # Append Dataframe in the list to one big dataframe!
        hexeurope_df = pd.concat(europe_list) 
    
    print('Country in Europe Table!')
    return hexeurope_df

hex_europe_list = []
for i in country_list:
    hex_europe_list.append(GetTopEurope(i))
    top_hex_europe = pd.concat(hex_europe_list)
    top_hex_europe = top_hex_europe.rename(columns={'hexeurope':'hex','street_name_count_hexeurope':'street_name_count'})
    top_hex_europe = top_hex_europe.reset_index()
    top_hex_europe = top_hex_europe.drop(columns='index')
    print("Europe Hex Table finish!")

print('Dataframe for top streets in Europe for each categories Ready')
print('Data Push to SQL')
top_hex_europe.to_sql("sbs_hex_streets", con=conn, if_exists='append', index=False)
print("Hex Europe in sql")


###  -------------------- FUNCTION TO GET TOP STREETS EACH COUNTRIES --------------------  ###
# -----------------------------------------------------------------------------------------  #
def TopCountryCount(data1,data2,country):
    
    top_country = []
    top_country_list = []
    
    country_shape = data1.loc[data1['country']==country]
    country_classification = data2.loc[data2['country']==country]
    country_join = country_classification.merge(country_shape, on=['name','country'])
    country_join = country_join.drop_duplicates()
    country_join = country_join.rename(columns={'country_x':'country'})
    
    top_country.append(country_join)
    data_all = pd.concat(top_country)
    
    # Count streets
    data_all['street_name_count'] = data_all.groupby(["name","classification",'country'])['name'].transform('count')
    top_country_df = data_all[['name','country','classification','sub_class','period_class','street_name_count']]
    
    for i in category_list:
        # Get all the different top 10 street for each category!
        filterdata_category = top_country_df.loc[top_country_df['classification']==i]
        #Country
        filterdata_category = filterdata_category.sort_values(['street_name_count'],ascending=False)
        top_country_streets = filterdata_category.drop_duplicates('name', keep='first')
        #Keep only the first occurance name of the 10 famous street names!
        top_country_streets = top_country_streets.head(10)
        # Append each category_df to list result
        top_country_list.append(top_country_streets)
        # Append Dataframe in the list to one big dataframe!
        top_country_streets_df = pd.concat(top_country_list)
    
    return top_country_streets_df
###  -------------------- FUNCTION TO ADD WIKI URL --------------------  ###
def AddWikipedia(country):
    data = TopCountryCount(shape,classification,country)
    # Merge the top results with the wikipedia url table
    wiki_join = data.merge(wikipedia, on=['name','country'])
    wiki_join = wiki_join.drop_duplicates()
    return wiki_join 

top_countries = []
for i in country_list:
    country = TopCountryCount(shape,classification,i)
    top_countries.append(country)
    top_country_df = pd.concat(top_countries)
    top_country_df = top_country_df.reset_index()
    top_country_df = top_country_df.drop(columns='index')
    
print('Dataframe for top streets in Countries for each categories Ready ')
print('Data Push to SQL')
top_country_df.to_sql("sbs_count_streets", con=conn, if_exists='append', index=False)
print("Country Streets in sql")




###  --------------------  FUNCTION TO GET TOP STREETS FOR EUROPE  --------------------   ###
# ----------------------------------------------------------------------------------------  #

def TopEuropeCount(data1,data2,country):
    
    top_europe = []

    country_shape = data1.loc[data1['country']==country]
    country_classification = data2.loc[data2['country']==country]
    country_join = country_classification.merge(country_shape, on=['name','country'])
    country_join = country_join.drop_duplicates()
    country_join = country_join.rename(columns={'country_x':'country'})
    
    top_europe.append(country_join)
    data_all = pd.concat(top_europe)

    data_all['street_name_count'] = data_all.groupby(["name","classification"])['name'].transform('count')
    top_europe_df = data_all[['name','country','classification','sub_class','period_class','street_name_count']]

    return top_europe_df

## Loop Through All Countries ##
top_europe = []

for i in country_list:
    countries = TopEuropeCount(shape,classification,i)
    top_europe.append(countries)
    top_europe_df = pd.concat(top_europe)

## Loop Through All Categories ##
top_europe_list = []

for i in category_list:
    # Get all the different top 10 street for each category!
    filterdata_category = top_europe_df.loc[top_europe_df['classification']==i]
    #Country
    filterdata_category = filterdata_category.sort_values(['street_name_count'],ascending=False)
    top_europe_streets = filterdata_category.drop_duplicates('name', keep='first')
    #Keep only the first occurance name of the 10 famous street names!
    top_europe_streets = top_europe_streets.head(10)
    # Append each category_df to list result
    top_europe_list.append(top_europe_streets)
    # Append Dataframe in the list to one big dataframe!
    top_eu_streets_df = pd.concat(top_europe_list)
    top_eu_streets_df = top_eu_streets_df.reset_index()
    
# For Belgium!
belgium = top_eu_streets_df[top_eu_streets_df['country']=='belgium']
belgium = belgium.drop(columns=['index'])
belgium['country'] = 'europe'
belgium['wikiurl'] = pd.np.nan
belgium['category'] = pd.np.nan

# Merge the top results with the wikipedia url table
wiki_europe = top_eu_streets_df.merge(wikipedia, on=['name','country'])
wiki_europe = wiki_europe.drop_duplicates(subset=['name','country'])
top_eu_streets_df = wiki_europe.drop(columns=['index'])
top_eu_streets_df['country'] = 'europe'

print('Dataframe for top streets in Europe for each categories Ready')
print('Push Data to SQL')
top_eu_streets_df.to_sql("sbs_count_streets", con=conn, if_exists='append', index=False)
belgium.to_sql("sbs_count_streets", con=conn, if_exists='append', index=False)
print("Europe Data in sql")

###   FUNCTION TO READ POLYGONS FOR EACH CITY AND APPEND HEX ID   ###
# ----------------------------------------------------------------  #
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
    
    #read polygons for cities in this country
    cities = getCities(country)
    polygonscities = gpd.GeoDataFrame()
    for city in cities:
        print(city)
        polygons = gpd.read_file('hexes/hex-city/'+country+'/'+city+'/'+city+'.json')
        polygons.columns = ["hex","rand","geometry"]
        polygons.loc[:, 'city'] = city
        polygonscities = polygonscities.append(polygons) 
        # Set crs for both dataframe
        gdf_points.crs = polygonscities.crs    

    #spatial join both where a points intersects with a polygon
    city_point_join = gpd.sjoin(gdf_points,polygonscities,op="intersects")
    city_point_join = city_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,11,13]]
    print(" -- CITY JOIN -- ")
    
    return city_point_join

###   FUNCTION TO GET TOP STREET FOR EACH CITY, EACH CATEGORY, EACH HEX ID   ###
# ---------------------------------------------------------------------------  #
def GetTopStreet(country):
    
    hex_list = []

    df_all = groupbycountry(shape,classification,country)

    #Create dataframe for each country, each category, each hexid
    df_hexcity = df_all[["name",'city',"classification","hex","sub_class","period_class"]]
    df_hexcity['street_name_count'] = df_hexcity.groupby(["name","classification","hex"])['name'].transform('count')
    
    print(str(country) + ' Table Ready!') 
    
    for i in category_list:
        # Get all the different top 5 streets for each category in each hexagons!
        filterdata_category_hex = df_hexcity.loc[df_hexcity['classification']==i]
    
        # Hex Country
        filterdata_category_hex_id = filterdata_category_hex.sort_values(['hex','street_name_count'],ascending=False)
        top_hex = filterdata_category_hex_id.drop_duplicates(subset=['name','hex'],keep='first')
        #Keep only the first occurance name of the 5 famous street names!
        top_hex = top_hex.groupby('hex').head(5)
        # Append each category_df to list result
        hex_list.append(top_hex) 
        # Append Dataframe in the list to one big dataframe!
        hex_df = pd.concat(hex_list) 
    
    print('City Hex Table finish!')
    return hex_df

###   FOR LOOP TO GET ALL HEX IN SAME DATAFRAME   ###
# ------------------------------------------------- #
country_list_city = ['belgium', 'italy', 'austria', 'switzerland', 'france']
hex_city_list = []
for i in country_list_city:
    city_df = GetTopStreet(i)
    hex_city_list.append(city_df)
    top_hex_city = pd.concat(hex_city_list)
    top_hex_city = top_hex_city.rename(columns={'city':'country'})
    top_hex_city = top_hex_city.reset_index()
    top_hex_city = top_hex_city.drop(columns='index')

print('Dataframe for top streets in City for each HEX for each categories Ready')
print('Data Push to SQL')
top_hex_city.to_sql("sbs_hex_streets_cities", con=conn, if_exists='append', index=False)
print("hex city in sql")



###  --------------------  FUNCTION TO GET TOP STREETS FOR CITIES  --------------------   ###
# ----------------------------------------------------------------------------------------  #

def GroupByCity(data1,data2,country):
    
    top_city_streets = []
    
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
    
    #read polygons for cities in this country
    cities = getCities(country)
    polygonscities = gpd.GeoDataFrame()
    for city in cities:
        print(city)
        polygons = gpd.read_file('hexes/hex-city/'+country+'/'+city+'/'+city+'.json')
        polygons.columns = ["hex","rand","geometry"]
        polygons.loc[:, 'city'] = city
        polygonscities = polygonscities.append(polygons) 
        # Set crs for both dataframe
        gdf_points.crs = polygonscities.crs    

    #spatial join both where a points intersects with a polygon
    city_point_join = gpd.sjoin(gdf_points,polygonscities,op="intersects")
    city_point_join = city_point_join.iloc[:,[0,1,2,3,4,5,6,7,8,11,13]]
    print(" -- CITY JOIN -- ")
            
    return city_point_join


## Loop Through All Countries ##
top_city = []

for i in country_list_city:
    cities = GroupByCity(shape,classification,i)
    
    # Count the streets for each city!
    cities['street_name_count'] = cities.groupby(["name","classification","city"])['name'].transform('count')
    top_city_streets = cities[['name','country','city','classification','sub_class','period_class','street_name_count']]
    top_city.append(top_city_streets)
    top_city_df = pd.concat(top_city)


city_list = []
for c in top_city_df.city:
    if c not in city_list:
        city_list.append(c)
    else:
        continue
print(city_list)

top_city_list = []

for c in city_list:
    for i in category_list:
        # Get all the different top 5 street for each category!
        filterdata_category = top_city_df.loc[top_city_df['city']==c]
        filterdata_category = filterdata_category.loc[filterdata_category['classification']==i]
        #Country
        filterdata_category = filterdata_category.sort_values(['city','street_name_count'],ascending=False)
        top_city_streets = filterdata_category.drop_duplicates(subset=['name','city'], keep='first')
        #Keep only the first occurance name of the 10 famous street names!
        top_city_streets = top_city_streets.head(5)
        # Append each category_df to list result
        top_city_list.append(top_city_streets)
        # Append Dataframe in the list to one big dataframe!
        top_city_streets_df = pd.concat(top_city_list)
        
        top_city_streets_df = top_city_streets_df.reset_index()

# For Belgium!
belgium = top_city_streets_df[top_city_streets_df['country']=='belgium']
belgium = belgium.drop(columns=['index','country'])
belgium = belgium.rename(columns={'city':'country'})
belgium['wikiurl'] = pd.np.nan
belgium['category'] = pd.np.nan

# Merge the top results with the wikipedia url table
wiki_city = top_city_streets_df.merge(wikipedia, on=['name','country'])
wiki_city = wiki_city.drop_duplicates(subset=['name','country','city'])
top_city_streets_df = wiki_city.drop(columns=['index','country'])
top_city_streets_df = top_city_streets_df.rename(columns={'city':'country'})

print('Dataframe for top streets in City for each categories Ready')
print('Data Push to SQL')
top_city_streets_df.to_sql("sbs_count_streets", con=conn, if_exists='append', index=False)
belgium.to_sql("sbs_count_streets", con=conn, if_exists='append', index=False)
print("hex city in sql")