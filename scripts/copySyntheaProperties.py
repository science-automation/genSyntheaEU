import os
from dotenv import load_dotenv
import time
from shutil import copyfile

# country list
countries = ["BE", "BG", "CY", "CZ", "DK", "DE", "EE", "GR", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

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
    file='synthea.properties'
    if os.path.exists(os.path.join(BASE_INPUT_DIRECTORY,file)):
        OUTPUT_DIRECTORY =  os.path.join(BASE_OUTPUT_DIRECTORY,country.lower())
        OUTPUT_DIRECTORY = OUTPUT_DIRECTORY + '/src/main/resources'
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)
        src = os.path.join(BASE_INPUT_DIRECTORY,file)
        dst = os.path.join(OUTPUT_DIRECTORY,file)
        copyfile(src, dst)
        with open(dst) as f:
            newText=f.read().replace('exporter.csv.export = false', 'exporter.csv.export = true').replace('generate.append_numbers_to_person_names = true','generate.append_numbers_to_person_names = true').replace('generate.geography.country_code = US','generate.geography.country_code = ' + country).replace('generate.payers.insurance_companies.medicare = Medicare','generate.payers.insurance_companies.medicare = National Health Service').replace('generate.payers.insurance_companies.medicaid = Medicaid','generate.payers.insurance_companies.medicaid = National Health Service').replace('generate.payers.insurance_companies.dual_eligible = Dual Eligible','generate.payers.insurance_companies.dual_eligible = National Health Service')
        with open(dst, "w") as f:
            f.write(newText)
