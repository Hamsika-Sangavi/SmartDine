import pandas as pd
import requests
import time

df = pd.read_pickle("data/zomato_with_sentiment.pkl")
locations = df["location"].unique()

geocoded = {}
headers = {"User-Agent": "SmartDine-College-Project"}

for loc in locations:
    query = f"{loc}, Bangalore, India"
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data:
            geocoded[loc] = (float(data[0]["lat"]), float(data[0]["lon"]))
            print(f"{loc}: {geocoded[loc]}")
        else:
            geocoded[loc] = (None, None)
            print(f"{loc}: NOT FOUND")
    except Exception as e:
        geocoded[loc] = (None, None)
        print(f"{loc}: ERROR - {e}")
    time.sleep(1)  # Nominatim rate limit: 1 request/second

geo_df = pd.DataFrame([
    {"location": loc, "latitude": lat, "longitude": lon}
    for loc, (lat, lon) in geocoded.items()
])
geo_df.to_pickle("data/location_geocodes.pkl")
print("\nSaved geocodes to data/location_geocodes.pkl")
print(f"Found: {geo_df['latitude'].notna().sum()} / {len(geo_df)}")