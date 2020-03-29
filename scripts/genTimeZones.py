import pandas as pd
import os
from dotenv import load_dotenv
import zipfile
import string

# capitalize the first char of each word to make consistent
def makeTitle(name):
    return string.capwords(name)

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']
# postal code base files
BASE_POSTAL_CODE_DIRECTORY    = os.environ['BASE_POSTAL_CODE_DIRECTORY']

# list of countries to be processed. cy and gr do  not have zip code files so maybe do manually
countries= ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]
columns=["country_code", "postal_code", "place_name", "admin_name1", "admin_code1", "admin_name2", "admin_code2", "admin_name3", "admin_code3", "latitude", "longitude", "accuracy"]

# load in the country timezones
zonedf = pd.read_csv(BASE_INPUT_DIRECTORY + '/country_timezone.csv', dtype='object')

# load in iso codes
isocode = pd.read_csv(BASE_INPUT_DIRECTORY + '/2019-2-SubdivisionCodes.csv', dtype='object')

for country in countries:
    print("Processing " + country)
    OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
    OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/geography'
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    # read the postal code file
    path_to_zip_file = BASE_POSTAL_CODE_DIRECTORY + '/' + country.lower() + ".zip"
    if os.path.exists(path_to_zip_file):
        tmppath = BASE_INPUT_DIRECTORY + "/tmp"
        if not os.path.exists(tmppath):
            os.makedirs(tmppath)
        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(tmppath)
        # load the file into a dataframe
        csvfile = tmppath + "/" + country + ".txt"
        df = pd.read_csv(csvfile, dtype='object', sep='\t', names=columns, header=None)
        if country == "GB":
            df = df[['country_code','admin_name2']].drop_duplicates()
            df = pd.merge(df, isocode, left_on='admin_name2', right_on='name', how='left')
            df = df.rename(columns={"admin_name2": "STATE", "isocodem": "ST"})
            df = df[['country_code','STATE','ST']].drop_duplicates()
            df = df.dropna()  # still dropping too many that dont have iso codes
        else:
            # get distinct 
            df = df[['country_code','admin_name1','admin_code1']].drop_duplicates()
            df = df.rename(columns={"admin_name1": "STATE", "admin_code1": "ST"})
            df = df.dropna()
        # join on country code
        df = pd.merge(df, zonedf, left_on='country_code', right_on='country_code', how='left')
        df = df.rename(columns={"std_full": 'TIMEZONE', 'std_abbr': 'TZ'})
        header = ["STATE","ST","TIMEZONE","TZ"]
        df['STATE'] = df['STATE'].apply(makeTitle)
        df.to_csv(os.path.join(OUTPUT_DIRECTORY,'timezones.csv'), columns = header, index=False, encoding='UTF-8')
