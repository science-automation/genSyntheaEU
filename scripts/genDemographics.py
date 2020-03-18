import pandas as pd
import os
import zipfile
from dotenv import load_dotenv
import ModelSyntheaPandas
import ModelData

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the city data
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that demographhic files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()
model_data = ModelData.ModelData()

# load the world cities into a dataframe
cities = pd.read_csv(BASE_INPUT_DIRECTORY + '/cities500.txt', dtype=model_data.model_schema['geoname'], sep='\t', encoding = "utf-8")
print(cities.dtypes)

# list of countries to be processed.  No FI since we have better data
countries= ["BE", "BG", "CY", "CZ", "DK", "DE", "EE", "GR", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

for country in countries:
    print("Processing: " + country)
    OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
    OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/geography'
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    # create synthea demographic df
    df = pd.DataFrame(columns=model_synthea.model_schema['demographics'].keys())
    # filter only cities in this country
    citieslocal = cities.loc[cities['country code'] == country]
    df['NAME'] = citieslocal['name']
    df['CTYNAME'] = citieslocal['name']
    df['STNAME'] = citieslocal['admin1 code']
    df['TOT_POP'] = citieslocal['population']
    # sort
    df = df.sort_values('CTYNAME')
    # save to disk
    df.to_csv(OUTPUT_DIRECTORY + '/demographics.csv', mode='w', header=True, index=True)
