import sqlite3
import json
import codecs

conn = sqlite3.connect('data.sqlite')
cur = conn.cursor()

cur.execute("SELECT * FROM Locations")
file = codecs.open('place.js', 'w', 'utf-8')
file.write("geoData = [\n")
count = 0
for row in cur:
    data = str(row[1].decode())
    try:
        js = json.loads(str(data))
    except:
        continue

    if not('status' in js and js['status'] == 'OK'):
        continue

    latitude = js['results'][0]['geometry']['location']['lat']
    longitude = js['results'][0]['geometry']['location']['lng']
    if latitude == 0 or longitude == 0: continue
    where = js['results'][0]['formatted_address']
    where = where.replace("'", "")
    try:
        print(where, latitude, longitude)
        count += 1
        if count > 1: file.write(",\n")
        output = "["+str(latitude)+","+str(longitude)+", '"+where+"']"
        file.write(output)
    except:
        continue

file.write("\n];\n")
cur.close()
file.close()
print(f"{count} records written to place.js")
print("Open place.html to view the data in a browser")