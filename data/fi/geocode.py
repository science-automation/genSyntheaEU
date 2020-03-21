# using here api to geocode locations
import requests
import sys
import os

# open address file
f=open("addresses.csv", "r")
lines=f.readlines()  

# open the file for writing
fg=open("addresses_geocoded.csv", "a")

apikey='26-F1lvtEvTcghTmwmATnczYWGOa7w8G5zXJHTuZhyI'
API_URL = 'https://geocoder.ls.hereapi.com/search/6.2/geocode.json'
counter=0

for line in lines: 
    if counter < 79665:
        counter=counter+1
        continue
    line = line.strip()
    line = line.replace('"','')
    address = line.split(';')[0]
    lineid = line.split(';')[1]
    params = {
        'language': 'en_us',
        'max_results': '1',
        'searchtext': address,
        'apikey': apikey
    }

    # Do the request and get the response data
    try: 
        req = requests.get(API_URL, params=params)
        res = req.json()
        location = res['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
    except:
        print("Could not get geocode for " + address)
        continue
    lat = location['Latitude']
    lon = location['Longitude']
    fg.write(lineid + ";" + str(lat) + ";" + str(lon) + "\n")
    counter = counter + 1
    print("Completed geocode for " + address + " count: " + str(counter))
    #if counter == 10:
    #    f.close()
    #    fg.close()
    #    sys.exit()
f.close()
fg.close()
