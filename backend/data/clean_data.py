import pandas as pd
import ast

df = pd.read_csv("data/zomato.csv")

# Drop columns we don't need
df = df.drop(columns=["url", "phone", "menu_item", "dish_liked", "listed_in(city)"])

# Clean rate: "4.1/5" -> 4.1, "NEW"/"-" -> NaN
def clean_rate(x):
    if isinstance(x, str) and "/" in x:
        try:
            return float(x.split("/")[0])
        except ValueError:
            return None
    return None

df["rate"] = df["rate"].apply(clean_rate)

# Clean cost: "1,200" -> 1200.0
df["approx_cost(for two people)"] = (
    df["approx_cost(for two people)"]
    .astype(str)
    .str.replace(",", "")
    .astype(float)
)

# Parse reviews_list string into actual list of review texts
def parse_reviews(x):
    try:
        parsed = ast.literal_eval(x)
        return [review_text for _, review_text in parsed]
    except (ValueError, SyntaxError):
        return []

df["reviews_parsed"] = df["reviews_list"].apply(parse_reviews)
df = df.drop(columns=["reviews_list"])

# Drop rows with no rating, drop duplicates
df = df.dropna(subset=["rate"])
df = df.drop_duplicates(subset=["name", "address"])

print("Final shape:", df.shape)
print(df[["name", "location", "rate", "approx_cost(for two people)", "cuisines"]].head(3).to_string())

df.to_pickle("data/zomato_clean.pkl")
print("Saved cleaned data to data/zomato_clean.pkl")