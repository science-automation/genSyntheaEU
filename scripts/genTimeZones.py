import pandas as pd
import os
import pathlib
from dotenv import load_dotenv

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

# list of countries to be processed
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "GR", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

# load the iso region file into a dataframe
df = pd.read_csv(BASE_INPUT_DIRECTORY + '/2019-2-SubdivisionCodes.csv', dtype='object', encoding = "cp1252")

# load in the country timezones
zonedf = pd.read_csv(BASE_INPUT_DIRECTORY + '/country_timezone.csv', dtype='object')

for country in countries:
    print("Processing " + country)
    OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
    OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/geography'
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    regions = df.loc[df['country'] == country]
    # write the timezones.csv file
    countryzone = zonedf.loc[zonedf['country_code'] == country]
    countryzone = countryzone.reset_index(drop=True)
    std_full = countryzone.at[0,"std_full"]
    std_abbr = countryzone.at[0,"std_abbr"]
    print(std_full, std_abbr)
    regions['TIMEZONE'] = std_full
    regions['TZ'] = std_abbr
    regions = regions.rename(columns={"name": "STATE", "isocodem": "ST"})
    header = ["STATE","ST","TIMEZONE","TZ"]
    regions.to_csv(OUTPUT_DIRECTORY + '/timezones.csv', columns = header, index=False, encoding='UTF-8')
