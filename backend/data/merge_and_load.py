import pandas as pd
import mysql.connector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

df = pd.read_pickle("data/zomato_with_amenities.pkl")
geo_df = pd.read_pickle("data/location_geocodes.pkl")

# Merge lat/long into main data
df = df.merge(geo_df, on="location", how="left")

# Keep one sample review per restaurant for "explainability" display, drop the rest
df["sample_review"] = df["reviews_parsed"].apply(lambda r: r[0][:300] if r else "")
df = df.drop(columns=["reviews_parsed"])

print("Final columns:", df.columns.tolist())
print("Final shape:", df.shape)
print(df.head(2).to_string())

# Create table
conn = get_connection()
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS restaurants")
cursor.execute("""
CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(500),
    location VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    online_order VARCHAR(10),
    book_table VARCHAR(10),
    rate FLOAT,
    votes INT,
    rest_type VARCHAR(255),
    cuisines VARCHAR(500),
    approx_cost FLOAT,
    listed_in_type VARCHAR(100),
     sentiment_score FLOAT,
    sample_review TEXT,
    review_summary TEXT,
        has_wifi BOOLEAN,
    has_parking BOOLEAN,
    is_veg_friendly BOOLEAN,
    wheelchair_accessible BOOLEAN,
    serves_alcohol BOOLEAN,
    live_music BOOLEAN,
    outdoor_seating BOOLEAN,
    has_vegan_options BOOLEAN,
    is_halal BOOLEAN,
    has_gluten_free BOOLEAN
)
""")
conn.commit()
print("Table created.")

# Insert rows
insert_query = """
INSERT INTO restaurants
(name, address, location, latitude, longitude, online_order, book_table,
  rate, votes, rest_type, cuisines, approx_cost, listed_in_type, sentiment_score, sample_review, review_summary,
  has_wifi, has_parking, is_veg_friendly, wheelchair_accessible, serves_alcohol,
 live_music, outdoor_seating, has_vegan_options, is_halal, has_gluten_free)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

rows = []
import math

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (bool, type(True))):
        return bool(v)
    if hasattr(v, "item"):  # catches numpy bool_, numpy int64, etc.
        return v.item()
    return v

rows = []
for _, r in df.iterrows():
    rows.append(tuple(clean_val(v) for v in (
        r["name"], r["address"], r["location"],
        r["latitude"], r["longitude"],
        r["online_order"], r["book_table"], r["rate"],
        int(r["votes"]) if pd.notna(r["votes"]) else 0,
        r["rest_type"], r["cuisines"],
        r["approx_cost(for two people)"],
                r["listed_in(type)"], r["sentiment_score"], r["sample_review"], r["review_summary"],
                      r["has_wifi"], r["has_parking"], r["is_veg_friendly"],
        r["wheelchair_accessible"], r["serves_alcohol"], r["live_music"],
        r["outdoor_seating"], r["has_vegan_options"], r["is_halal"], r["has_gluten_free"]
    )))

cursor.executemany(insert_query, rows)
conn.commit()
print(f"Inserted {cursor.rowcount} rows.")

cursor.close()
conn.close()