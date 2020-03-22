import os
from dotenv import load_dotenv
import pandas as pd
import time
import ModelSyntheaPandas
import sys
import requests
import unicodedata

def getAsciiString(demo):
        return unicodedata.normalize('NFD', demo).encode('ascii', 'ignore').decode("utf-8")

# fix emergency yes/no case
def emergencyValue(value):
    if value == "yes":
        return "Yes"
    elif value == "no":
        return "No"
    else:
        return value

# take df and add geo data based on lat and lon
def addGeoInfo(df, apikey, columns, regions):
    API_URL = 'https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.json'
    df2 = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        lat = row['LAT']
        lon = row['LON']
        prox = str(lat) + "," + str(lon)
        params = {
            'language': 'en_us',
            'max_results': '1',
            'prox': prox,
            'mode': 'retrieveAreas',
            'apikey': apikey
        }
        try:
            req = requests.get(API_URL, params=params)
            res = req.json()
            row['city'] = res['Response']['View'][0]['Result'][0]['Location']['Address']['City']
            row['zip'] = res['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']
            county = res['Response']['View'][0]['Result'][0]['Location']['Address']['County']
            country = getAsciiString(county)
            state = res['Response']['View'][0]['Result'][0]['Location']['Address']['State']
            state = getAsciiString(state)
            if state in regions:
                row['state'] = state
            elif county in regions:
                row['state'] = county
            else:
                row['state'] = county
            dftemp = row.to_frame().T
        except:
            dftemp = row.to_frame().T
        req = requests.get(API_URL, params=params)
        df2 = pd.concat([df2,dftemp])
    return df2


# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']
# region code 
BASE_REGION_DIRECTORY   = os.environ['BASE_REGION_DIRECTORY']
# Hospital base id
HOSPITAL_BASE_ID        = os.environ['HOSPITAL_BASE_ID']
# Urgent care base id
URGENT_CARE_BASE_ID     = os.environ['URGENT_CARE_BASE_ID']
# Primary care base id
PRIMARY_CARE_BASE_ID    = os.environ['PRIMARY_CARE_BASE_ID']
# apikey
APIKEY                  = os.environ['APIKEY']

print('BASE_INPUT_DIRECTORY     =' + BASE_INPUT_DIRECTORY)
print('BASE_OUTPUT_DIRECTORY    =' + BASE_OUTPUT_DIRECTORY)
print('BASE_REGION_DIRECTORY    =' + BASE_REGION_DIRECTORY)
print('HOSPITAL_BASE_ID         =' + HOSPITAL_BASE_ID)
print('URGENT_CARE_BASE_ID      =' + URGENT_CARE_BASE_ID)
print('PRIMARY_CARE_BASE_ID     =' + PRIMARY_CARE_BASE_ID)

# countries list. There is better data for FI so doing that one later
countries = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()

for country in countries:
    print("Processing country: " + country)
    # get a list of regions
    if os.path.exists(BASE_REGION_DIRECTORY):
        file = BASE_REGION_DIRECTORY + "/" + country.lower() + '/src/main/resources/geography/timezones.csv'
        regiondf = pd.read_csv(file)
        regions = regiondf.STATE.unique()
    else:
        sys.exit()

    # load the csv
    file='./hospital_'+ country.lower() + '.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        hospitals = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), compression=None)
        # map OSM data synthea data
        # create hospitals.csv and urgent_care_facilities.csv
        # urgent_care_facilities has emergency=yes
        OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
        OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/providers'
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)
        df = pd.DataFrame(columns=model_synthea.model_schema['hospitals'].keys())
        df['name'] = hospitals['name']
        df['id'] = df.index + int(HOSPITAL_BASE_ID)
        df['LAT'] =  hospitals['lat']
        df['LON'] = hospitals['lon']
        if 'phone' in hospitals.columns:
            df['phone'] = hospitals['phone']
        if 'addr:housenumber' in hospitals.columns and 'addr:street' in hospitals.columns:
            hospitals['addr:street'] = hospitals['addr:street'].astype('str')
            hospitals['addr:housenumber'] = hospitals['addr:housenumber'].astype('str')
            df['address'] = hospitals['addr:street'] + " " +  hospitals['addr:housenumber']
        if 'emergency' in  hospitals.columns:
            df['emergency'] = hospitals['emergency'].apply(emergencyValue)
        df = addGeoInfo(df, APIKEY, model_synthea.model_schema['hospitals'].keys(), regions)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True, encoding='UTF-8')
        # create urgent_care_facilities by filtering on emergency
        df = df.loc[df['emergency'].str.lower() == 'yes']
        df['id'] = df.index + int(URGENT_CARE_BASE_ID)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'urgent_care_facilities.csv'), mode='w', header=True, index=True, encoding='UTF-8')
    else:
        print("File " + file + " does not exist")

    # load clinics file and create primary_care_facilities for synthea
    file='./clinic_'+ country.lower() + '.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        clinics = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), compression=None)
        # create primary_care_facilities.csv
        df = pd.DataFrame(columns=model_synthea.model_schema['primary_care_facilities'].keys())
        df['name'] = clinics['name']
        df['id'] = df.index + int(HOSPITAL_BASE_ID)
        df['LAT'] =  clinics['lat']
        df['LON'] = clinics['lon']
        df['hasSpecialties'] = 'False'
        if 'phone' in clinics.columns:
            df['phone'] = clinics['phone']
        if 'addr:housenumber' in clinics.columns and 'addr:street' in clinics.columns:
            clinics['addr:street'] = clinics['addr:street'].astype('str')
            clinics['addr:housenumber'] = clinics['addr:housenumber'].astype('str')
            df['address'] = clinics['addr:street'] + " " + clinics['addr:housenumber']
        df = addGeoInfo(df, APIKEY, model_synthea.model_schema['primary_care_facilities'].keys(), regions)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'primary_care_facilities.csv'), mode='w', header=True, index=True, encoding='UTF-8')
    else:
        print("File " + file + " does not exist")
    sys.stdout.flush()

