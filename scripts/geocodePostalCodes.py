# using here api to geocode postal codes if they dont have region/state
import requests
import sys
import os
import pandas as pd
from dotenv import load_dotenv
import glob
import codecs
import ModelData
import zipfile

def isNaN(string):
    return string != string

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

# list of countries to be processed.  GR and CY have different format and processed later. FI is using data from Finnish posti
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

# load the synthea model
model_data = ModelData.ModelData()

# create output directory if it does not exist
if not os.path.exists(BASE_OUTPUT_DIRECTORY):
    os.makedirs(BASE_OUTPUT_DIRECTORY)

# set api key and api url
apikey='26-F1lvtEvTcghTmwmATnczYWGOa7w8G5zXJHTuZhyI'
API_URL = 'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json'

for country in countries:
    print("Processing: " + country)
    OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
    OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/geography'
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    # make a temp directory to unpack the zip
    path_to_zip_file = BASE_INPUT_DIRECTORY + '/' + country.lower() + ".zip"
    if os.path.exists(path_to_zip_file):
        tmppath = BASE_INPUT_DIRECTORY + "/tmp"
        if not os.path.exists(tmppath):
             os.makedirs(tmppath)
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
             zip_ref.extractall(tmppath)
        # load the file into a dataframe
        csvfile = tmppath + "/" + country + ".txt"
        df = pd.read_csv(csvfile, names=model_data.model_schema['postalcodes'].keys(), dtype=model_data.model_schema['postalcodes'], sep='\t', header=None, encoding='utf-8')
        for index, row in df.iterrows():
            for mode in ['retrieveAll']:
                lat = row['latitude']
                lon = row['longitude']
                prox = str(lat) + "," + str(lon)
                params = {
                    'language': 'en_us',
                     'max_results': '1',
                     'prox': prox,
                     'mode': mode,
                     'apikey': apikey
                }

                if isNaN(row['admin_name1']) and (country=='IE' or country=='SI' or country=='SE'):
                    print("geocoding " + prox)
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
