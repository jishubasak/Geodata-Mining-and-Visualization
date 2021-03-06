import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = input('Insert Google API Key: '
# If you have a Google Places API key, enter it here
# Format of api_key = 'AIzaSy___IDByT70'

serviceurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

#Making connection with SQLite:
conn = sqlite3.connect('geodata.sqlite') # geodata.sqlite DB file stored in the directory 
cur = conn.cursor()

#Modificiation of DB file:
cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fh = open("where.data") # where.data is the list of user fed locations. By default, its a list of random locations more specific to universities.
count = 0
for line in fh:
    if count > 200 : 
        print('Retrieved 200 locations, restart to retrieve more')
        break

    address = line.strip()
    print('')
    cur.execute("SELECT geodata FROM Locations WHERE address= ?",
        (memoryview(address.encode()), )) # Using memoryview to increase execution time.

    try:
        data = cur.fetchone()[0]
        print("Found in database ",address) # Avoiding duplication
        continue
    except:
        pass

    parms = dict()
    parms["query"] = address
    if api_key is not False: parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))
    count = count + 1

    try:
        js = json.loads(data)
    except:
        print(data)  # We print in case unicode causes an error.
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print('==== Failure To Retrieve ====')
        print(data)
        break

    cur.execute('''INSERT INTO Locations (address, geodata)
            VALUES ( ?, ? )''', (memoryview(address.encode()), memoryview(data.encode()) ) )
    conn.commit()
    if count % 10 == 0 :
        print('Pausing for a bit...')
        time.sleep(5)

print("Run geodump.py to read the data from the database so you can visualize it on a map.")