import pandas as pd
import os
import zipfile
from dotenv import load_dotenv
import ModelSyntheaPandas
import ModelData
import unicodedata

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

for country in countries:
    print("Processing: " + country)
