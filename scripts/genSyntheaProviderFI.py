# -*- coding: utf-8 -*-
import os
import pandas as pd
import ModelSyntheaPandas

BASE_INPUT_DIRECTORY="./"
OUTPUT_DIRECTORY="./"
file='sote.csv'

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()

if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
    healthsites = pd.read_csv(os.path.join(BASE_INPUT_DIRECTORY,file), dtype='object', sep=';', encoding='utf-8', compression=None)
    # fix data in some columns
    healthsites['Katuosoite'] = healthsites['Katuosoite'].str.encode('utf-8')
    healthsites['Postitoimipaikka'] = healthsites['Postitoimipaikka'].str.encode('utf-8')
    healthsites['Postinumero'] = healthsites['Postinumero'].str.encode('utf-8')

# write a list of all addresses so that we can geocode them
df = pd.DataFrame(columns=['address'])
df['id'] = healthsites['Tunniste']
df['address'] = healthsites['Katuosoite'] + " " + healthsites['Postitoimipaikka'] + " " + healthsites['Postinumero']
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'addresses.csv'), mode='w', header=True, sep=';', index=False, encoding='utf-8')

df = pd.DataFrame(columns=model_synthea.model_schema['hospitals'].keys())
#Sairaalatjjj
df['id'] = healthsites['Tunniste']
name = u"Pitkä nimi"
df['name'] = healthsites[name]
df['address'] = healthsites['Katuosoite']
df['city'] = healthsites['Postitoimipaikka']
df['zip'] = healthsites['Postinumero']
df['phone'] = healthsites['Puhelinnumero']
df['type'] = healthsites['Sektori']
df['ownership'] = healthsites['Org.Yks.lyhenne']
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'hospitals.csv'), mode='w', header=True, index=True, encoding='utf-8')
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'urgent_care_facilities.csv'), mode='w', header=True, index=True, encoding='utf-8')

df = pd.DataFrame(columns=model_synthea.model_schema['primary_care_facilities'].keys())
df['id'] = healthsites['Tunniste']
df['name'] = healthsites[name]
df['address'] = healthsites['Katuosoite']
df['city'] = healthsites['Postitoimipaikka']
df['zip'] = healthsites['Postinumero']
df['phone'] = healthsites['Puhelinnumero']
df['hasSpecialties'] = 'False'
df.to_csv(os.path.join(OUTPUT_DIRECTORY,'primary_care_facilities.csv'), mode='w', header=True, index=True, encoding='utf-8')
