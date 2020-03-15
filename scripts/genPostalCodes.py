import pandas as pd
import os
import pathlib
import zipfile

# build dir
builddir = '../build'

# load the iso region file into a dataframe
isodf = pd.read_csv('../data/2019-2-SubdivisionCodes.csv', dtype='object', encoding = "cp1252")

# list of countries to be processed.  GR and CY have different format and processed later
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

columns=["country_code", "postal_code", "place_name", "admin_name1", "admin_code1", "admin_name2", "admin_code2", "admin_name3", "admin_code3", "latitude", "longitude", "accuracy"]

for country in countries:
    print("Processing: " + country)
    # make a temp directory to unpack the zip
    tmppath = builddir + "/tmp"
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    path_to_zip_file = "../../postalcodes/" + country.lower() + ".zip"
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(tmppath)
    # load the file into a dataframe
    csvfile = tmppath + "/" + country + ".txt"
    df = pd.read_csv(csvfile, dtype='object', sep='\t', names=columns, header=None)
    # make the output directory
    path = builddir + "/" + country.lower() + "/src/main/resources/geography"
    if not os.path.exists(path):
        os.makedirs(path)
    # get the region iso code
    df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
    # change some column names
    df = df.rename(columns={"admin_name1": "USPS", "isocodem": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
    # clean up
    df['NAME'] = df['NAME'].str.rstrip()
    # write the zipcodes.csv file
    header = ["USPS","ST","NAME","ZCTA5","LAT","LON"]
    df.to_csv(path + '/zipcodes.csv', columns = header, encoding='UTF-8')
 
countries=["GR"]
countries=["CY"]