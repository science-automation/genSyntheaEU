import os
from dotenv import load_dotenv
import time
from shutil import copyfile

# country list. Don't process fi
countries = ["BE", "BG", "CY", "CZ", "DK", "DE", "EE", "GR", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "SE", "NO", "GB"]

# ------------------------
# load env
# ------------------------
load_dotenv(verbose=True)

# set output directory
# Path to the directory containing the input healthsites files
BASE_INPUT_DIRECTORY    = os.environ['BASE_INPUT_DIRECTORY']
# Path to the base directory that provider files will be written to
BASE_OUTPUT_DIRECTORY   = os.environ['BASE_OUTPUT_DIRECTORY']

print('BASE_INPUT_DIRECTORY     =' + BASE_INPUT_DIRECTORY)
print('BASE_OUTPUT_DIRECTORY    =' + BASE_OUTPUT_DIRECTORY)

for country in countries:
    print("Copying synthea properties file for " + country)
    # load the properties file
    file='insurance_companies.csv'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
        OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources/payers'
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)
        src = os.path.join(BASE_INPUT_DIRECTORY,file)
        dst = os.path.join(OUTPUT_DIRECTORY,file)
        copyfile(src, dst)
        with open(dst) as f:
            newText=f.read().replace('exporter.csv.export = false', 'exporter.csv.export = true')
        with open(dst, "w") as f:
            f.write(newText)
