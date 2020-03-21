# -*- coding: utf-8 -*-
import os
import pandas as pd
import ModelSyntheaPandas
import sys

# given date in synthea format return the year
def splitName(name):
    return name.split(',')[0].strip()

def getSector(name):
    if name == '1 Julkinen':
        return 'Public'
    elif name == '2 yksityinen':
        return 'Private'
    else:
        return ""

BASE_INPUT_DIRECTORY="./"
OUTPUT_DIRECTORY="./"

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()

file='sote.csv'
if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
    healthsites = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), dtype='object', sep=';', encoding='utf-8', compression=None)
    # fix data in some columns
    healthsites['Katuosoite'] = healthsites['Katuosoite'].str.encode('utf-8')
    healthsites['Postitoimipaikka'] = healthsites['Postitoimipaikka'].str.encode('utf-8')
    healthsites['Postinumero'] = healthsites['Postinumero'].str.encode('utf-8')
else:
    print("Could not find input healthsites file")
    sys.exit()

name = u"Pitkä nimi"
# join the geocode data
geocoded = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,'addresses_geocoded.csv'), dtype='object', sep=';', encoding='utf-8', compression=None)
healthsites = pd.merge(healthsites, geocoded, on='Tunniste', how='left')
# remove discontinued sites
healthsites = healthsites.loc[~healthsites[name].str.contains('LOPETETTU', case=False)].reset_index()

# write a list of all addresses so that we can geocode them
#df = pd.DataFrame(columns=['address'])
#df['id'] = healthsites['Tunniste']
#df['address'] = healthsites['Katuosoite'] + " " + healthsites['Postitoimipaikka'] + " " + healthsites['Postinumero']
#df.to_csv(os.path.join(OUTPUT_DIRECTORY,'addresses.csv'), mode='w', header=True, sep=';', index=False, encoding='utf-8')

df = pd.DataFrame(columns=model_synthea.model_schema['hospitals'].keys())
hospitals = healthsites.loc[healthsites[name].str.contains('sairaala', case=False)].reset_index()
hospitals = hospitals.loc[~hospitals[name].str.contains('terveys|hammas|polik|laboratorio|dialyysi|kliininen|apteekki|lääkekeskus|optiikka', case=False)].reset_index(drop=True)
hospitals = hospitals[hospitals['lat'].notna()].reset_index(drop=True)
df['id'] = hospitals['Tunniste']
df['name'] = hospitals[name].apply(splitName)
df['address'] = hospitals['Katuosoite']
df['city'] = hospitals['Postitoimipaikka']
df['zip'] = hospitals['Postinumero']
df['phone'] = hospitals['Puhelinnumero']
df['type'] = hospitals['Sektori'].apply(getSector)
df['ownership'] = hospitals['Org.Yks.lyhenne']
df['LAT'] = hospitals['lat']
df['LON'] = hospitals['lon']
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True, encoding='utf-8')
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'urgent_care_facilities.csv'), mode='w', header=True, index=True, encoding='utf-8')

df = pd.DataFrame(columns=model_synthea.model_schema['primary_care_facilities'].keys())
clinics = healthsites.loc[healthsites[name].str.contains('terveys|polik|kliininen', case=False)].reset_index()
clinics = clinics[clinics['lat'].notna()].reset_index(drop=True)
df['id'] = clinics['Tunniste']
df['name'] = clinics[name].apply(splitName)
df['address'] = clinics['Katuosoite']
df['city'] = clinics['Postitoimipaikka']
df['zip'] = clinics['Postinumero']
df['phone'] = clinics['Puhelinnumero']
df['LAT'] = clinics['lat']
df['LON'] = clinics['lon']
df['hasSpecialties'] = 'False'
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'primary_care_facilities.csv'), mode='w', header=True, index=True, encoding='utf-8')
