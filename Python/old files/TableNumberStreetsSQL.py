import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')

countrieslist = ["austria","belgium","france","germany","italy","netherlands","portugal","spain","switzerland"]
language = ["de",['nl,fr,de'],"fr","de",['it,de'],"nl","pt",['es,ca,gl,eu'],['de,fr,it']]
street = []
for i in range(0,len(countrieslist)):
	street.append(0)

c = {'Country':countrieslist, "language":language,'Streets':street,'StreetsDrop':street,'Streetsunique':street}

countries = pd.DataFrame(c)

countries.to_sql('sbs_countries_streets',engine,if_exists = "replace")

