import requests
import pandas as pd
import json
from pandas.io.json import json_normalize

endpoint = 'https://gateway-lon.watsonplatform.net/natural-language-understanding/api/v1/analyze'
data = {'text': 'king Arthur, king Arthur, Italie, Italie, Albert 1er, Albert 1er','features': {"entities": {'limit': 5,'mentions': False,'sentiment': False,'emotion':False, 'dbpedia_resource':True} } }

auth = ('apikey', 'JHtzNHapQGHHiobssLEyz5ECX5sfZ0yAP9VvwJindgRb')

# This defines that we want our answer as a JSON file
headers = {'Content-Type': 'application/json'}

# We need to select the version of the API we are using
params = (('version', '2018-11-16'),)

r = requests.post(endpoint, headers=headers, params=params, data=json.dumps(data), auth=auth)

print(r.status_code)

print(r.json())

entity = json_normalize(r.json()['entities'])

print(entity[["type","text"]])