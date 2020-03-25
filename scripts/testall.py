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
basedir = sys.argv[1]

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the city data
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']

# list of countries to be processed.
countries= ["BE", "BG", "CY", "CZ", "DK", "DE", "EE", "GR", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

for country in countries:
    print("Processing: " + country)
    zonefile = BASE_INPUT_DIRECTORY + "/" + country.lower() + "/src/main/resources/geography/timezones.csv"
    print(zonefile)
    df = pd.read_csv(zonefile)
    regions = df.STATE.unique()
    print(regions)
    os.chdir(basedir + '/s/synthea')
    os.system("cp -R ../synthea-international/" + country.lower() + "/* .")
    for region in regions:
        # run synthea
        print("Running synthea for region " + region)
        os.system("./run_synthea -p 5 " + "\"" + region + "\"")
