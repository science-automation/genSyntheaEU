import pandas as pd
import os
import zipfile
from dotenv import load_dotenv
import ModelSyntheaPandas
import ModelData
import unicodedata
import sys

if len(sys.argv) <2:
    print("BASEDIR should be set")
    sys.exit()

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the city data
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that demographhic files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

# list of countries to be processed.
countries= ["BE", "BG", "CY", "CZ", "DK", "DE", "EE", "GR", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

os.chdir(basedir + '/s/ETL-Synthea-Python/output')
for country in countries:
    print("Processing: " + country)
    zonefile = BASE_INPUT_DIRECTORY + "/" + country.lower() + "/src/main/resources/geography/timezones.csv"
    print(zonefile)
    df = pd.read_csv(zonefile)
    regions = df.STATE.unique()
    print(regions)
    for region in regions:
        # run synthea
        print("Running synthea for region " + region)
        os.system("./run_synthea -p 5 " + region)
