import pandas as pd
import os
import zipfile
from dotenv import load_dotenv

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

# load the iso region file into a dataframe
isodf = pd.read_csv(ISO_REGION_DIRECTORY + '/2019-2-SubdivisionCodes.csv', dtype='object', encoding = "cp1252")

# list of countries to be processed.  GR and CY have different format and processed later. FI is using data from Finnish posti
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

columns=["country_code", "postal_code", "place_name", "admin_name1", "admin_code1", "admin_name2", "admin_code2", "admin_name3", "admin_code3", "latitude", "longitude", "accuracy"]

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
        df = pd.read_csv(csvfile, dtype='object', sep='\t', names=columns, header=None)
        # get the region iso code
        df = pd.merge(df,isodf,left_on='admin_name1', right_on='name', how='left')
        # change some column names
        df = df.rename(columns={"admin_name1": "USPS", "admin_code1": "ST", "place_name": "NAME", "postal_code": "ZCTA5", "latitude": "LAT", "longitude": "LON"})
        # clean up
        df['NAME'] = df['NAME'].str.rstrip()
        # write the zipcodes.csv file
        header = ["USPS","ST","NAME","ZCTA5","LAT","LON"]
        df.to_csv(OUTPUT_DIRECTORY + '/zipcodes.csv', columns = header, encoding='UTF-8')
 
countries=["GR"]
countries=["CY"]
