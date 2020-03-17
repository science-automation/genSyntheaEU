import os
from dotenv import load_dotenv
import time
from shutil import copyfile

def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print('"{old_string}" not found in {filename}.'.format(**locals()))
            return
    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        s = f.read()
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)

# country list
countries = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

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
        inplace_change(dst,"exporter.csv.export = false","exporter.csv.export = true")
        inplace_change(dst,"generate.append_numbers_to_person_names = true","generate.append_numbers_to_person_names = false")
        inplace_change(dst,"generate.geography.country_code = US","generate.geography.country_code = " + country)
