import requests
import re
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()

url = 'https://fr.wikipedia.org/wiki/Jean_Mermoz?action=raw'

t = requests.get(url)
text = t.text

text.find('Infobox')
start = text.find('{{Infobox') + 10

if (start == 9):
    #return empty list of necesarry length
    print(0)
else: 
    newtext = text[start:]
    
    stop = newtext.find("}}\n\n''")
    if (stop == -1 ):
        stop = newtext.find("}}\n''")
    info = newtext[:stop]
    
    #print(re.search("(\A<!--).+(-->)", "",info))
    
   # categorynum = info.find('\n')
    if info.find('|') < info.find('\n'):
        categorynum = info.find('\n')
    else:
        categorynum = info.find('|')
        
    print(categorynum)
    category = info[0:categorynum]
    
    # if( category[-1] == " " or category[-2] == "}]"):
    #  	category = info[0:categorynum-1]

    keys = []
    values = []
    
    keys.append("category")
    values.append(category.encode('utf-8'))

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



print(keys)
print(values)
    #print(dict(zip(keys,values)))