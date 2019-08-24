from shapely import wkb
from sqlalchemy import create_engine
import pandas as pd
from geopandas import GeoDataFrame


engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()


sql = """SELECT * FROM ucfnama.sbs_wales LIMIT 5;"""
df = pd.read_sql(sql, engine)

def to_linestring(line):
	return wkb.loads(line, hex=True)
df['geometry'] = df['geometry'].apply(to_linestring)

geodf = GeoDataFrame(df, geometry='geometry')

#https://gis.stackexchange.com/questions/119752/reading-postgis-geometry-with-shapely