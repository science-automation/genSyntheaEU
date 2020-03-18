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
    citieslocal = citieslocal.sort_values('name').reset_index()
    df['NAME'] = citieslocal['name']
    df['ID'] = df.index
    df['COUNTY'] = df.index
    df['STNAME'] = citieslocal['admin1 code']
    df['CTYNAME'] = citieslocal['name']
    df['TOT_POP'] = citieslocal['population']
    df['TOT_MALE'] = '.5'
    df['TOT_FEMALE'] = '.5'
    df['WHITE'] =
    df['HISPANIC'] =
    df['BLACK'] =
    df['ASIAN'] =
    df['NATIVE'] =
    df['OTHER'] =
    df['1'] =
    df['2'] =
    df['3'] =
    df['4'] =
    df['5'] =
    df['6'] =
    df['7'] =
    df['8'] =
    df['9'] =
    df['10'] =
    df['11'] =
    df['12'] =
    df['13'] =
    df['14'] =
    df['15'] =
    df['16'] =
    df['17'] =
    df['18'] =
    df['00..10'] =
    df['10..15'] =
    df['15..25'] =
    df['25..35'] =
    df['35..50'] =
    df['50..75'] =
    df['75..100'] =
    df['100..150'] =
    df['150..200'] =
    df['200..999'] =
    df['LESS_THAN_HS'] =
    df['HS_DEGREE'] =
    df['SOME_COLLEGE'] =
    df['BS_DEGREE'] =

    # sort
    df = df.sort_values('CTYNAME')
    # save to disk
    df.to_csv(OUTPUT_DIRECTORY + '/demographics.csv', mode='w', encoding = 'utf-8', header=True, index=False)
