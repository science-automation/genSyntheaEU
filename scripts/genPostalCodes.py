import pandas as pd
import os
import zipfile
from dotenv import load_dotenv
import string
import ModelSyntheaPandas
import ModelData
import codecs
import json

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

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the postalcode files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']
# path to iso region file
ISO_REGION_DIRECTORY    = os.environ['ISO_REGION_DIRECTORY']
# base geocode directory
BASE_GEOCODE_DIRECTORY  = os.environ['BASE_GEOCODE_DIRECTORY']

model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()
model_data = ModelData.ModelData()

# load the iso region file into a dataframe
isodf = pd.read_csv(ISO_REGION_DIRECTORY + '/2019-2-SubdivisionCodes.csv', dtype='object', encoding = "cp1252")

# list of countries to be processed.  GR and CY have different format and processed later. FI is using data from Finnish posti
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

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
        df = pd.read_csv(csvfile, dtype=model_data.model_schema['postalcodes'], sep='\t', names=model_data.model_schema['postalcodes'].keys(), header=None)
        # get the region iso code
        if (country=='GB'):
            df = pd.merge(df,isodf,left_on='admin_name2', right_on='name', how='left')
            df = df.rename(columns={"admin_name2": "USPS", "isocodem": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        elif (country=='IE'):
            df = addGeoInfoLocal(df, model_data.model_schema['postalcodes'].keys(), BASE_GEOCODE_DIRECTORY)
            df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
            df = df.rename(columns={"admin_name1": "USPS", "isocodem": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        elif (country=='SI'):
            df = addGeoInfoLocal(df, model_data.model_schema['postalcodes'].keys(), BASE_GEOCODE_DIRECTORY)
            df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
            df = df.rename(columns={"admin_name1": "USPS", "isocodem": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        elif (country=='LT'):
            df['admin_name1']=df['admin_name1'].str.replace(' County','')
            df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
            df = df.rename(columns={"admin_name1": "USPS", "admin_code1": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        else:
            df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
            df = df.rename(columns={"admin_name1": "USPS", "admin_code1": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        # clean up
        df['NAME'] = df['NAME'].str.rstrip()
        df = df[df['USPS'].notna()]
        df['USPS'] = df['USPS'].apply(makeTitle)
        if country == "NO":
            df['USPS'] = df['USPS'].str.replace('Oslo County','Oslo')
        if (country=='LV'):
            df['USPS'] = df['USPS'].str.replace('Nov.','Novads')
        if (country=='BE'):
            df['USPS'] = df['USPS'].str.replace('Bruxelles-capitale','Bruxelles')
        if (country=='BG'):
            df['USPS'] = df['USPS'].apply(fixBG)
        # write the zipcodes.csv file
        header = ["USPS","ST","NAME","ZCTA5","LAT","LON"]
        df.to_csv(OUTPUT_DIRECTORY + '/zipcodes.csv', columns=model_synthea.model_schema['postalcodes'].keys(), encoding='UTF-8')
 
countries=["GR"]
countries=["CY"]
