import pandas as pd
import re
from rapidfuzz import process, fuzz

zomato = pd.read_pickle("data/zomato_with_summary.pkl")
tripadvisor = pd.read_csv("data/Bengaluru_Restaurants.csv")

def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = name.split(" - ")[0]
    name = name.split(",")[0]
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def has_keyword(text, keyword):
    if not isinstance(text, str):
        return False
    return keyword.lower() in text.lower()

tripadvisor["norm_name"] = tripadvisor["name"].apply(normalize_name)

# Features column flags
tripadvisor["has_wifi"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "wifi"))
tripadvisor["has_parking"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "parking"))
tripadvisor["wheelchair_accessible"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "wheelchair"))
tripadvisor["serves_alcohol"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "alcohol"))
tripadvisor["live_music"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "live music"))
tripadvisor["outdoor_seating"] = tripadvisor["Features"].apply(lambda x: has_keyword(x, "outdoor seating"))

# DietaryRestrictions column flags
tripadvisor["is_veg_friendly"] = tripadvisor["DietaryRestrictions"].apply(lambda x: has_keyword(x, "vegetarian"))
tripadvisor["has_vegan_options"] = tripadvisor["DietaryRestrictions"].apply(lambda x: has_keyword(x, "vegan"))
tripadvisor["is_halal"] = tripadvisor["DietaryRestrictions"].apply(lambda x: has_keyword(x, "halal"))
tripadvisor["has_gluten_free"] = tripadvisor["DietaryRestrictions"].apply(lambda x: has_keyword(x, "gluten free"))

zomato["norm_name"] = zomato["name"].apply(normalize_name)
trip_names = tripadvisor["norm_name"].tolist()

def find_match(name, threshold=88):
    if not name:
        return None
    result = process.extractOne(name, trip_names, scorer=fuzz.ratio, score_cutoff=threshold)
    if result:
        matched_name, score, idx = result
        return idx
    return None

print("Matching restaurants... this may take a minute.")
zomato["match_idx"] = zomato["norm_name"].apply(find_match)

matched_count = zomato["match_idx"].notna().sum()
print(f"Matched {matched_count} / {len(zomato)} restaurants ({matched_count/len(zomato)*100:.1f}%)")

AMENITY_FIELDS = [
    "has_wifi", "has_parking", "wheelchair_accessible", "serves_alcohol",
    "live_music", "outdoor_seating", "is_veg_friendly", "has_vegan_options",
    "is_halal", "has_gluten_free",
]

def get_field(idx, field):
    if pd.isna(idx):
        return None
    return tripadvisor.iloc[int(idx)][field]

for field in AMENITY_FIELDS:
    zomato[field] = zomato["match_idx"].apply(lambda idx: get_field(idx, field))

print(zomato[["name"] + AMENITY_FIELDS].dropna(subset=["has_wifi"]).head(5).to_string())

zomato = zomato.drop(columns=["match_idx", "norm_name"])
zomato.to_pickle("data/zomato_with_amenities.pkl")
print("\nSaved to data/zomato_with_amenities.pkl")