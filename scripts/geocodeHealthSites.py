# using here api to geocode locations
import requests
import sys
import os
import pandas as pd
from dotenv import load_dotenv
import glob
import codecs

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

# create output directory if it does not exist
if not os.path.exists(BASE_OUTPUT_DIRECTORY):
    os.makedirs(BASE_OUTPUT_DIRECTORY)

# set api key and api url
apikey=''
API_URL = 'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json'

# get list of all files
if os.path.exists(BASE_INPUT_DIRECTORY):
    files = glob.glob(BASE_INPUT_DIRECTORY + '/*.csv')
    for file in files:
        print("Processing " + file)
        df = pd.read_csv(file, encoding='utf-8')
        for index, row in df.iterrows():
            for mode in ['retrieveAll']:
                lat = row['lat']
                lon = row['lon']
                prox = str(lat) + "," + str(lon)
                params = {
                    'language': 'en_us',
                     'max_results': '1',
                     'prox': prox,
                     'mode': mode,
                     'apikey': apikey
                }

                # Do the request and get the response data
                try: 
                    req = requests.get(API_URL, params=params)
                    res = req.json()
                    filename = BASE_OUTPUT_DIRECTORY + '/' + prox + ".json"
                    file = codecs.open(filename, "w", "utf-8")
                    file.write(req.text)
                    file.close()
                except:
                    print("Could not reverse geocode for " + prox)
