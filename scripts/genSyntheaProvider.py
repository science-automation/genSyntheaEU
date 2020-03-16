import os
from dotenv import load_dotenv
import pandas as pd
import time
import ModelSyntheaPandas

countries = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY    = os.environ['BASE_OUTPUT_DIRECTORY']
print('BASE_INPUT_DIRECTORY     =' + BASE_INPUT_DIRECTORY)
print('BASE_OUTPUT_DIRECTORY    =' + BASE_OUTPUT_DIRECTORY)

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()

for country in countries:
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
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True)
        df['name'] = hospitals['name']
        df['LAT'] =  hospitals['lat']
        df['LON'] = hospitals['lon']
        if 'phone' in hospitals.columns:
            df['phone'] = hospitals['phone']
        if 'addr:housenumber' in hospitals.columns and 'addr:street' in hospitals.columns:
            #df['address'] = hospitals['addr:housenumber'] + " " + hospitals['addr:street']
            df['address'] = hospitals['addr:street']
        if 'emergency' in  hospitals.columns:
            df['emergency'] = hospitals['emergency']
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True)
        # create urgent_care_facilities by filtering on emergency
        df = df.loc[df['emergency'].str.lower() == 'yes']
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'urgent_care_facilities.csv'), mode='w', header=True, index=True)
    else:
        print("File " + file + " does not exist")

    # load clinics file and create primary_care_facilities for synthea
    file='./clinic_'+ country.lower() + '.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        clinics = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), compression=None)
        # create primary_care_facilities.csv
        df = pd.DataFrame(columns=model_synthea.model_schema['primary_care_facilities'].keys())
        df['name'] = clinics['name']
        df['LAT'] =  clinics['lat']
        df['LON'] = clinics['lon']
        df['hasSpecialties'] = 'False'
        if 'phone' in clinics.columns:
            df['phone'] = clinics['phone']
        if 'addr:housenumber' in clinics.columns and 'addr:street' in clinics.columns:
            #df['address'] = clinics['addr:housenumber'] + " " + clinics['addr:street']
            df['address'] = clinics['addr:street']
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'primary_care_facilities.csv'), mode='w', header=True, index=True)
    else:
        print("File " + file + " does not exist")
