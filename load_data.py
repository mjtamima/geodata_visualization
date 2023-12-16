import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = False

if api_key is False:
    api_key = 42
    inurl = "http://py4e-data.dr-chuck.net/json?"
else:
    inurl = "https://maps.googleapis.com/maps/api/geocode/json?"

sqfile = sqlite3.connect('data.sqlite')
cur = sqfile.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)""")

# Fix SSL certificate errors
ct = ssl.create_default_context()
ct.check_hostname = False
ct.verify_mode = ssl.CERT_NONE

location_file = open('place.data')
count = 0
for line in location_file:
    if count > 200:
        print("Retrieved 200 locations, restart to retrieve more")
        break

    address = line.strip()
    print('')
    cur.execute("SELECT geodata from Locations WHERE address=?", (memoryview(address.encode()), ))

    try:
        data = cur.fetchone()[0]
        print("Found in database", address)
        continue
    except:
        pass

    addict = dict()
    addict['address'] = address
    if api_key is not False: addict['key'] = api_key
    url = inurl + urllib.parse.urlencode(addict)

    print('Retrieving', url)
    uhandle = urllib.request.urlopen(url, context=ct)
    data = uhandle.read().decode()
    print(f"Retrieved {len(data)} characters", {data[:20].replace('\n', ' ')})
    count += 1

    try:
        js = json.loads(data)
    except:
        print(data)
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS'):
        print("****Failed to retrieve****")
        print(data)
        break

    cur.execute("""INSERT INTO Locations (address, geodata) VALUES (?,?)""",
                (memoryview(address.encode()), memoryview(data.encode())))
    sqfile.commit()
    if count % 10 == 0:
        print("Pausing for a bit...")
        time.sleep(5)

print("Run geojs.py to read data from the database for visualizing it on a map. Have fun!")
