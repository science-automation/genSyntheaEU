import pandas as pd
import os
import sys
import zipfile
from dotenv import load_dotenv
import ModelSyntheaPandas
import ModelData
import unicodedata
import string

def getAsciiString(demo):
    return unicodedata.normalize('NFD', demo).encode('ascii', 'ignore').decode("utf-8")

# capitalize the first char of each word to make consistent
def makeTitle(name):
    return string.capwords(name)

# make sure city can be found in the zip codes
def matchZip(name, postalcode):
    postalcode = postalcode[postalcode['NAME'].notna()]
    citydf = postalcode[postalcode['NAME'].str.contains(name)]
    citydfascii = postalcode[postalcode['NAME'].str.contains(getAsciiString(name))]
    if (len(citydf) > 0):
        return name
    elif (len(citydfascii) > 0): 
        return getAsciiString(name)
    else:
        # return a string so we can filter it out later 
        return "nopostalcode"
    
# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the city data
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that demographhic files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']
#
BASE_POSTALCODE_DIRECTORY  = os.environ['BASE_POSTALCODE_DIRECTORY']

# load the synthea model
model_synthea = ModelSyntheaPandas.ModelSyntheaPandas()
model_data = ModelData.ModelData()

# load the world cities into a dataframe
cities = pd.read_csv(BASE_INPUT_DIRECTORY + '/cities500.txt', dtype=model_data.model_schema['geoname'], sep='\t', encoding = "utf-8")

# load data so that we can convert geonames fips to region name
divisions = pd.read_csv(BASE_INPUT_DIRECTORY + '/divisions.csv', dtype=model_data.model_schema['divisions'], sep=';', encoding = "utf-8")

# list of countries to be processed.  No FI since we have better data
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

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
    divisionslocal = divisions.loc[divisions['ISO-3166-1'] == country]
    postalcode =  pd.read_csv(BASE_POSTALCODE_DIRECTORY + '/' + country.lower() + '/src/main/resources/geography/zipcodes.csv', encoding = "utf-8")
    if country == 'GB':
        citieslocal = pd.merge(citieslocal, postalcode[['USPS','ST', 'NAME']], left_on='name', right_on='NAME', how='inner')
        citieslocal = citieslocal.rename(columns={"USPS": "Name of Subdivision"})
    elif country == 'IE':
        citieslocal = pd.merge(citieslocal, postalcode[['USPS','ST', 'NAME']], left_on='name', right_on='NAME', how='inner')
        citieslocal = citieslocal.rename(columns={"USPS": "Name of Subdivision"})
    elif country == 'SI':
        citieslocal = pd.merge(citieslocal, postalcode[['USPS','ST', 'NAME']], left_on='name', right_on='NAME', how='inner')
        citieslocal = citieslocal.rename(columns={"USPS": "Name of Subdivision"})
    else:
        citieslocal = pd.merge(citieslocal, divisionslocal[['Fips', 'Name of Subdivision']], left_on='admin1 code', right_on='Fips', how='left')
    df['NAME'] = citieslocal['name'].apply(matchZip,args=(postalcode,))
    df['ID'] = df.index
    df['COUNTY'] = df.index
    df['STNAME'] = citieslocal['Name of Subdivision'].apply(makeTitle)
    df['POPESTIMATE2015'] = citieslocal['population']
    df['CTYNAME'] = df['NAME']
    df['TOT_POP'] = citieslocal['population']
    df['TOT_MALE'] = '.5'
    df['TOT_FEMALE'] = '.5'
    df['WHITE'] = '1.0'
    df['HISPANIC'] = '0.0'
    df['BLACK'] = '0.0'
    df['ASIAN'] = '0.0'
    df['NATIVE'] = '0.0'
    df['OTHER'] = '0.0'
    df['1'] = '0.07714804356595402'
    df['2'] = '0.07714804356595402'
    df['3'] = '0.07714804356595402'
    df['4'] = '0.07714804356595402'
    df['5'] = '0.03408632513110125'
    df['6'] = '0.04356595401371521'
    df['7'] = '0.05465913674868899'
    df['8'] = '0.06353368293666802'
    df['9'] = '0.07462686567164178'
    df['10'] = '0.06111335215812828'
    df['11'] = '0.07583703106091166'
    df['12'] = '0.07079467527228721'
    df['13'] = '0.06575231948366277'
    df['14'] = '0.06514723678902784'
    df['15'] = '0.05344897135941912'
    df['16'] = '0.030859217426381605'
    df['17'] = '0.021581282775312627'
    df['18'] = '0.01956434045986285'
    df['00..10'] = '0.19'
    df['10..15'] = '0.1145'
    df['15..25'] = '0.3'
    df['25..35'] = '0.2'
    df['35..50'] = '0.1'
    df['50..75'] = '0.055'
    df['75..100'] = '0.0265'
    df['100..150'] = '0.008'
    df['150..200'] = '0.005'
    df['200..999'] = '0.001'
    df['LESS_THAN_HS'] = '0.4481645824929407'
    df['HS_DEGREE'] =  '0.036506655909640987'
    df['SOME_COLLEGE'] = '0.409035901573215'
    df['BS_DEGREE'] = '0.10629286002420331'

    # filter out cities that dont have a zip code
    print("   Number of cities before filtering those that do not have zip code: " + str(len(df)))
    df = df[~df['NAME'].str.contains("nopostalcode")]
    print("   Number of cities after filtering those that do not have zip code: " + str(len(df)))

    # sort
    df = df.sort_values('CTYNAME')

    # country specific processing
    if country == 'EE':
        df['STNAME'] = df['STNAME'].str.replace('County', 'Maakond')

    # save to disk
    df.to_csv(OUTPUT_DIRECTORY + '/demographics.csv', mode='w', encoding = 'utf-8', header=True, index=False)
    sys.stdout.flush()
