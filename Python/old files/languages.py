import pandas as pd 
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()


info = pd.read_excel('Excel/languages.xlsx','Info')
info.to_sql('sbs_info',con= conn, if_exists='replace',index=False)

category = pd.read_excel('Excel/languages.xlsx','Category')
category.to_sql('sbs_category',con= conn, if_exists='replace',index=False)

