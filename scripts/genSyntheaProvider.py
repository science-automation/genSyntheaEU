import os
from dotenv import load_dotenv
import pandas as pd
import time
import ModelSyntheaPandas
import sys
import requests
import unicodedata
import codecs
import json
import string

def getAsciiString(demo):
    return unicodedata.normalize('NFD', demo).encode('ascii', 'ignore').decode("utf-8")

# capitalize the first char of each word to make consistent
def makeTitle(name):
    if isNaN(name):
        return name
    else:
        return string.capwords(name)

def isNaN(string):
    return string != string

# fix emergency yes/no case
def emergencyValue(value):
    if value == "yes":
        return "Yes"
    elif value == "no":
        return "No"
    else:
        return value

# take df and add geo data from downloaded data
def addGeoInfoLocal(df, columns, regions, geodatadir):
    df2 = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        lat = row['LAT']
        lon = row['LON']
        prox = str(lat) + "," + str(lon)
        # open the file for this if it exists
        geofile = prox + ".json"
        if os.path.exists(os.path.join(geodatadir, geofile)):
            with codecs.open(os.path.join(geodatadir, geofile), 'r', encoding='utf8') as f:
                res = json.load(f)
            #print(res['Response']['View'][0]['Result'][0]['Location']['Address'])
            if res['Response']['View']:
                address = res['Response']['View'][0]['Result'][0]['Location']['Address']
            else:
                address = {}
            if 'City' in address:
                row['city'] = res['Response']['View'][0]['Result'][0]['Location']['Address']['City']
            if 'PostalCode' in address:
                row['zip'] = res['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']
            if 'County' in address:
                county = res['Response']['View'][0]['Result'][0]['Location']['Address']['County']
            if 'State' in address:
                state = res['Response']['View'][0]['Result'][0]['Location']['Address']['State']
            if 'county' in locals():
                for region in regions:
                    if region == county:
                        row['state'] = county 
                    elif region == getAsciiString(county):
                        row['state'] = getAsciiString(county)
            if 'state' in locals():
                for region in regions:
                    if region == state:
                        row['state'] = state
                    elif region == getAsciiString(state):
                        row['state'] = getAsciiString(state)
            #if isNaN(row['state']):
            #    print("Did not find state for " + county + " " + state)
            # set address
            if row['address'] == 'nan nan':
                if 'Street' in address and 'HouseNumber' in address:
                    street = res['Response']['View'][0]['Result'][0]['Location']['Address']['Street']
                    number = res['Response']['View'][0]['Result'][0]['Location']['Address']['HouseNumber']
                    row['address'] = street + " " + number
                else:
                    row['address'] = ''
            #if 'nan' in row['address']:
            #    row['address'] = row['address'].replace('nan','')
            dftemp = row.to_frame().T
        else:
            dftemp = row.to_frame().T
        df2 = pd.concat([df2,dftemp])
    return df2        

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
            state = res['Response']['View'][0]['Result'][0]['Location']['Address']['State']
            if state in regions:
                row['state'] = state
            elif getAsciiString(state) in regions:
                row['state'] = getAsciiString(state)
            elif county in regions:
                row['state'] = county
            elif getAsciiString(county) in regions:
                row['state'] = getAsciiString(county)
            else:
                row['state'] = county
            dftemp = row.to_frame().T
        except:
            dftemp = row.to_frame().T
        #req = requests.get(API_URL, params=params) only use if need to debug
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
# Base geocode data
BASE_GEOCODE_DIRECTORY  = os.environ['BASE_GEOCODE_DIRECTORY']
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
print('BASE_GEOCODE_DIRECTORY   =' + BASE_GEOCODE_DIRECTORY)
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
        regiondf = pd.read_csv(file, encoding ='utf-8')
        regions = regiondf.STATE.unique()
    else:
        sys.exit()

    # load the csv
    file='hospital_'+ country.lower() + '.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        hospitals = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), compression=None)
        # add doctors and clinics for now until we get better hospital data
        doctorsfile = 'doctors_' + country.lower() + '.csv'
        if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,doctorsfile)):
            doctors = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,doctorsfile), compression=None)
            hospitals = pd.concat([hospitals,doctors], axis=0, ignore_index=True)
        clinicsfile = 'clinics_' + country.lower() + '.csv'
        if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,clinicsfile)):
            clinics = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,clinicsfile), compression=None)
            hospitals = pd.concat([hospitals,clinics], axis=0, ignore_index=True)
        # map OSM data synthea data
        # create hospitals.csv and urgent_care_facilities.csv
        # urgent_care_facilities has emergency=yes  (when we get better data but for now keep all)
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
        df = addGeoInfoLocal(df, model_synthea.model_schema['hospitals'].keys(), regions, BASE_GEOCODE_DIRECTORY)
        df['state'] = df['state'].apply(makeTitle)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True, encoding='UTF-8')
        # create urgent_care_facilities by filtering on emergency
        #df = df.loc[df['emergency'].str.lower() == 'yes']  keep all until we get better data
        df['id'] = df.index + int(URGENT_CARE_BASE_ID)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'urgent_care_facilities.csv'), mode='w', header=True, index=True, encoding='UTF-8')
    else:
        print("File " + file + " does not exist")

    # load clinics file and create primary_care_facilities for synthea
    clinicsfile='clinic_'+ country.lower() + '.csv'
    doctorsfile='doctors_' + country.lower() + '.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,clinicsfile)) or os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,doctorsfile)):
        if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,clinicsfile)): 
            clinics = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), compression=None)
        if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,doctorsfile)):
            doctors = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,doctorsfile), compression=None)
        primary = pd.concat([clinics,doctors], axis=0, ignore_index=True)
        # create primary_care_facilities.csv
        df = pd.DataFrame(columns=model_synthea.model_schema['primary_care_facilities'].keys())
        df['name'] = primary['name']
        df['id'] = df.index + int(PRIMARY_CARE_BASE_ID)
        df['LAT'] =  primary['lat']
        df['LON'] = primary['lon']
        df['hasSpecialties'] = 'False'
        if 'phone' in primary.columns:
            df['phone'] = primary['phone']
        if 'addr:housenumber' in primary.columns and 'addr:street' in primary.columns:
            primary['addr:street'] = primary['addr:street'].astype('str')
            primary['addr:housenumber'] = primary['addr:housenumber'].astype('str')
            df['address'] = primary['addr:street'] + " " + primary['addr:housenumber']
        df = addGeoInfoLocal(df, model_synthea.model_schema['primary_care_facilities'].keys(), regions, BASE_GEOCODE_DIRECTORY)
        df['state'] = df['state'].apply(makeTitle)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'primary_care_facilities.csv'), mode='w', header=True, index=True, encoding='UTF-8')
    else:
        print("File " + file + " does not exist")
    sys.stdout.flush()

