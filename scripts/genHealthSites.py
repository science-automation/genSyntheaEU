import overpy
import pandas as pd
import time

def make_query(country, amenity):
    outtype="[out:json][timeout:300];"
    area="(area[\"ISO3166-1\"=\"" + country + "\"][admin_level=2]; )->.country;"
    query =  "(node[\"amenity\"=\"" + amenity + "\"](area.country);way[\"amenity\"=\"" + amenity + "\"](area.country);relation[\"amenity\"=\"" + amenity + "\"](area.country););"
    extra = "(._;>;);"
    output = "out center;"
    return outtype + area + query + extra + output

def extract_keys(result):
    # look through ways and extract all keys
    keylist = {}
    for way in result.ways:
        keys = way.tags.keys()
        for key in keys:
            keylist[key] = "temp"
    keylist['lat'] = "temp"
    keylist['lon'] = 'temp'
    keys = keylist.keys()
    return keylist.keys()

api = overpy.Overpass()
amenity_types = ["hospital", "dentist", "pharmacy", "clinic", "dialysis"]
countries = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "ES", "FR", "HR", "IT", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "NO", "GB"]

for country in countries:
    for amenity in amenity_types:
        print("Processing " + amenity + " for country " + country)
        overpass_query = make_query(country, amenity)
        passing=False
        while not passing:
           try:
               result = api.query(overpass_query)
               passing=True
           except OverpassTooManyRequests:
               print("Sleeping to avoid rate limit")
               time.sleep(30)
        result = api.query(overpass_query)
        keys = extract_keys(result)
        df = pd.DataFrame(columns=keys)
        for way in result.ways:
            temp = way.tags
            temp['lat'] = way.nodes[0].lat
            temp['lon'] = way.nodes[0].lon
            dftemp = pd.DataFrame(temp, index=[0], columns=keys)
            df = df.append(dftemp)
        # if the amenity does not have a name, let's filter it out
        df = df[df['name'].notnull()]
        df.to_csv(amenity + '_' + country.lower() + '.csv', mode='w', header=True, index=False, encoding = 'utf-8')
