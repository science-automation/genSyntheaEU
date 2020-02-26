import pandas as pd
import os
import pathlib

# build dir
builddir = '../build'

# load the iso region file into a dataframe
df = pd.read_csv('../data/2019-2-SubdivisionCodes.csv', dtype='object', encoding = "cp1252")

# load in the country timezones
zonedf = pd.read_csv('../data/country_timezone.csv', dtype='object')

# list of countries to be processed
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "GR", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

for country in countries:
    print(country)
    regions = df.loc[df['country'] == country]
    path = builddir + "/" + country.lower() + "/src/main/resources/geography"
    if not os.path.exists(path):
        os.makedirs(path)
    # write the timezones.csv file
    countryzone = zonedf.loc[zonedf['country_code'] == country]
    countryzone = countryzone.reset_index(drop=True)
    std_full = countryzone.at[0,"std_full"]
    std_abbr = countryzone.at[0,"std_abbr"]
    print(std_full, std_abbr)
    #regions['timezone'] = 
