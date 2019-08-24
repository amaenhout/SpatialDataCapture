from sqlalchemy import create_engine
import pandas as pd

print("Wikipedia")
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()
print("SQL connected")

table = 'sbs_belgium'
nl =  pd.read_sql("select * from %(table)s ",con = conn,params= {'table':table})
