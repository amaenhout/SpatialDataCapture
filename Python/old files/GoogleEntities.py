# Imports the Google Cloud client library
import six
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from sqlalchemy import create_engine
import pandas as pd
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/arthurmaehout/GoogleDrive/UniversityCollegeLondon/Courses/Trm2/SpatialDataCapture/Assessment/Python/My First Project-80bab47ff5ab.json"

engine = create_engine('mysql+pymysql://ucfnama:dixavuvoyu@dev.spatialdatacapture.org:3306/ucfnama')
conn = engine.connect()


sql = """SELECT * FROM ucfnama.sbs_names where country = 'france' LIMIT 100;"""
df = pd.read_sql(sql, engine)
print("data read from sql ")
text =""
for name in df["name"]:
    if (text == ""):
        text = "'" + name +"'"
    else:
        text = text + ',' "'" + name + "'"

print("text var ready")
client = language.LanguageServiceClient()

if isinstance(text, six.binary_type):
    text = text.decode('utf-8')

# Instantiates a plain text document.
document = types.Document(
    content=text,
    type=enums.Document.Type.PLAIN_TEXT)

# Detects entities in the document. You can also analyze HTML with:
#   document.type == enums.Document.Type.HTML
entities = client.analyze_entities(document).entities

name = []
type = []
salince = []
wikipediaurl = []
mid = []

for entity in entities:
    entity_type = enums.Entity.Type(entity.type)
    # print('=' * 20)
    # print(u'{:<16}: {}'.format('name', entity.name))
    # print(u'{:<16}: {}'.format('type', entity_type.name))
    # print(u'{:<16}: {}'.format('salience', entity.salience))
    # print(u'{:<16}: {}'.format('wikipedia_url',
    #       entity.metadata.get('wikipedia_url', '-')))
    # print(u'{:<16}: {}'.format('mid', entity.metadata.get('mid', '-')))
    
    name.append(entity.name)
    type.append(entity_type.name)
    salince.append(entity.salience)
    wikipediaurl.append(entity.metadata.get('wikipedia_url', '-'))
    mid.append(entity.metadata.get('mid', '-'))

print("google api ready ")
df = {'name':name,'type':type,'salince':salince,'wikipediaurl':wikipediaurl,'mid':mid}
data = pd.DataFrame(df)
data.to_sql("sbs_google", con=conn, if_exists='replace', index=False)
