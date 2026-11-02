import pandas as pd

geo_df = pd.read_pickle("data/location_geocodes.pkl")

manual_fixes = {
    "ITPL Main Road, Whitefield": (12.9957, 77.7579),  # same area as Whitefield
    "Rammurthy Nagar": (13.0180, 77.6600),               # near Kalyan Nagar/CV Raman Nagar
    "Sadashiv Nagar": (13.0060, 77.5807),                 # near Malleshwaram
}

for loc, (lat, lon) in manual_fixes.items():
    geo_df.loc[geo_df["location"] == loc, "latitude"] = lat
    geo_df.loc[geo_df["location"] == loc, "longitude"] = lon

print("Remaining missing:", geo_df["latitude"].isna().sum())
geo_df.to_pickle("data/location_geocodes.pkl")
print("Updated and saved.")