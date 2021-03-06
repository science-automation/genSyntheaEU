# -*- coding: utf-8 -*-
import pandas as pd
import os
from dotenv import load_dotenv
import zipfile
import string
import ModelSyntheaPandas
import ModelData
import codecs
import json
import sys

# capitalize the first char of each word to make consistent
def makeTitle(name):
    if isNaN(name):
        return name
    else:
        return string.capwords(name)

def fixBG(name):
    value = name.split('/')
    if len(value) == 2:
        return value[0].strip()
    else:
        return name

def isNaN(string):
    return string != string

# take df and add geo data from downloaded data if postal code file has no state data
def addGeoInfoLocal(df, columns, geodatadir):
    df2 = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        prox = str(lat) + "," + str(lon)
        # open the file for this if it exists
        geofile = prox + ".json"
        if os.path.exists(os.path.join(geodatadir, geofile)):
            with codecs.open(os.path.join(geodatadir, geofile), 'r', encoding='utf8') as f:
                res = json.load(f)
            if res['Response']['View']:
                address = res['Response']['View'][0]['Result'][0]['Location']['Address']
            else:
                address = {}
            #print(res['Response']['View'][0]['Result'][0]['Location']['Address'])
            if 'County' in address:
                county = res['Response']['View'][0]['Result'][0]['Location']['Address']['County']
            if isNaN(row['admin_name1']):
                row['admin_name1'] = county
            dftemp = row.to_frame().T
        else:
            dftemp = row.to_frame().T
        df2 = pd.concat([df2,dftemp])
    return df2

# fix for poland to use local name
def plUseLocalName(state):
    plregion = {
        "Kujawsko-Pomorskie": "Kujawsko-Pomorskie",
        "Łódź Voivodeship": "Łódzkie",
        "Lublin": "Lubelskie",
        "Lubusz": "Lubuskie",
        "Lesser Poland": "Małopolskie",
        "Greate Poland": "Wielkopolskie",
        "Mazovia": "Mazowieckie",
        "Opole Voivodeship": "Opolskie",
        "Subcarpathia": "Podkarpackie",
        "Podlasie": "Podlaskie",
        "Pomerania": "Pomorskie",
        "Silesia": "Śląskie",
        "Lower Silesia": "Dolnośląskie",
        "Świętokrzyskie": "Świętokrzyskie",
        "Warmia-Masuria":  "Warmińsko-Mazurskie",
        "Greater Poland": "Wielkopolskie",
        "West Pomerania": "Zachodniopomorskie"
    }
    if state in plregion:
        return plregion[state]
    else:
        print("Not found for: " + state)
        return state

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY          = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY         = os.environ['BASE_OUTPUT_DIRECTORY']
# postal code base files
BASE_POSTALCODE_DIRECTORY     = os.environ['BASE_POSTALCODE_DIRECTORY']
# base geocode directory
BASE_GEOCODE_DIRECTORY        = os.environ['BASE_GEOCODE_DIRECTORY']

model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()
model_data = ModelData.ModelData()

# list of countries to be processed. cy and gr do  not have zip code files so maybe do manually
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

# load in the country timezones
zonedf = pd.read_csv(BASE_INPUT_DIRECTORY + '/country_timezone.csv', dtype='object')

# load in iso codes
isocode = pd.read_csv(BASE_INPUT_DIRECTORY + '/2019-2-SubdivisionCodes.csv', dtype='object')

for country in countries:
    print("Processing " + country)
    OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
    OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/geography'
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    # read the postal code file
    path_to_zip_file = BASE_POSTALCODE_DIRECTORY + '/' + country.lower() + ".zip"
    if os.path.exists(path_to_zip_file):
        #print("file exists")
        tmppath = BASE_INPUT_DIRECTORY + "/tmp"
        if not os.path.exists(tmppath):
            os.makedirs(tmppath)
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmppath)
        # load the file into a dataframe
        csvfile = tmppath + "/" + country + ".txt"
        df = pd.read_csv(csvfile, dtype=model_data.model_schema['postalcodes'], sep='\t', names=model_data.model_schema['postalcodes'].keys(), header=None)
        if country == "GB":
            df = df[['country_code','admin_name2']].drop_duplicates()
            df = pd.merge(df, isocode, left_on='admin_name2', right_on='name', how='left')
            df = df.rename(columns={"admin_name2": "STATE", "isocodem": "ST"})
            df = df[['country_code','STATE','ST']].drop_duplicates()
            df = df[df['STATE'].notna()]
        elif country == 'IE':
            df = addGeoInfoLocal(df, model_data.model_schema['postalcodes'].keys(), BASE_GEOCODE_DIRECTORY)
            df = pd.merge(df, isocode, left_on='admin_name1', right_on='name', how='left')
            df = df[['country_code','admin_name1','isocodem']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "isocodem": "ST"})
        elif country == 'SI':
            df = addGeoInfoLocal(df, model_data.model_schema['postalcodes'].keys(), BASE_GEOCODE_DIRECTORY)
            df = pd.merge(df, isocode, left_on='admin_name1', right_on='name', how='left')
            df = df[['country_code','admin_name1','isocodem']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "isocodem": "ST"})
        elif country == 'LT':
            df['admin_name1']=df['admin_name1'].str.replace(' County','')
            df = df[['country_code','admin_name1','admin_code1']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "admin_code1": "ST"})
            df = df[df['STATE'].notna()]
        elif country == 'PL':
            df['admin_name1']=df['admin_name1'].apply(plUseLocalName)
            df = df[['country_code','admin_name1','admin_code1']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "admin_code1": "ST"})
            df = df[df['STATE'].notna()]
        else:
            df = df[['country_code','admin_name1','admin_code1']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "admin_code1": "ST"})
            df = df[df['STATE'].notna()]
        # join on country code
        df = pd.merge(df, zonedf, left_on='country_code', right_on='country_code', how='left')
        df = df.rename(columns={"std_full": 'TIMEZONE', 'std_abbr': 'TZ'})
        header = ["STATE","ST","TIMEZONE","TZ"]
        df['STATE'] = df['STATE'].apply(makeTitle)
        if country == "BG":
            df['STATE'] = df['STATE'].apply(fixBG)
        if country == "NO":
            df['STATE'] = df['STATE'].str.replace('Oslo County','Oslo')
        if country == 'LV':
            df['STATE'] = df['STATE'].str.replace('Nov.','Novads')
        if (country=='BE'):
            df['STATE'] = df['STATE'].str.replace('Bruxelles-capitale','Bruxelles')
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'timezones.csv'), columns = header, index=False, encoding='UTF-8')
        sys.stdout.flush()
