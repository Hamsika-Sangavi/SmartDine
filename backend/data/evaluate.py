import os
import sys
import time
import requests
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

API = "http://127.0.0.1:8000"


def pct(values, p):
    s = sorted(values)
    return s[min(len(s) - 1, int(round(p / 100 * (len(s) - 1))))]


# ---------- 1. Data quality and sentiment check ----------
conn = get_connection()
cur = conn.cursor(dictionary=True)
cur.execute("SELECT rate, sentiment_score, latitude, longitude, has_wifi, review_summary FROM restaurants")
df = pd.DataFrame(cur.fetchall())
cur.close()
conn.close()

print("=" * 60)
print("1. DATA AND SENTIMENT CHECK")
print("=" * 60)
print(f"Total restaurants:               {len(df)}")
print(f"With map coordinates:            {df['latitude'].notna().mean() * 100:.1f}%")
print(f"With amenity data (2nd dataset): {df['has_wifi'].notna().mean() * 100:.1f}%")
print(f"With review summary:             {df['review_summary'].notna().mean() * 100:.1f}%")
print(f"Average rating:                  {df['rate'].mean():.2f}")
print(f"Average sentiment score:         {df['sentiment_score'].mean():.2f}")

valid = df.dropna(subset=["rate", "sentiment_score"])
print(f"\nPearson correlation (rating vs sentiment):  {valid['rate'].corr(valid['sentiment_score']):.3f}")
print(f"Spearman correlation (rating vs sentiment): {valid['rate'].rank().corr(valid['sentiment_score'].rank()):.3f}")
high = valid[valid["rate"] >= 4.0]["sentiment_score"].mean()
low = valid[valid["rate"] < 3.0]["sentiment_score"].mean()
print(f"Mean sentiment, restaurants rated >= 4.0:   {high:.3f}")
print(f"Mean sentiment, restaurants rated <  3.0:   {low:.3f}")

# ---------- 2. Ranking sanity check ----------
print("\n" + "=" * 60)
print("2. RANKING SANITY CHECK (top 10 vs all matches)")
print("=" * 60)

queries = [
    {"cuisine": "North Indian", "location": "Koramangala", "budget": 800},
    {"cuisine": "Chinese", "budget": 500},
    {"cuisine": "Cafe", "location": "Indiranagar"},
    {"budget": 1000},
    {"cuisine": "Biryani", "location": "Whitefield"},
    {"location": "Indiranagar", "nearby": True, "budget": 700},
]

for q in queries:
    r = requests.post(f"{API}/recommend", json={**q, "limit": 10000}, timeout=60).json()
    res = r["results"]
    if not res:
        print(f"{q} -> no results")
        continue
    top = res[:10]
    top_avg = sum(x["rate"] for x in top if x["rate"] is not None) / len(top)
    all_avg = sum(x["rate"] for x in res if x["rate"] is not None) / len(res)
    print(f"{str(q):<75} matches={len(res):<4} top10 avg rating={top_avg:.2f}  all-match avg={all_avg:.2f}")

# ---------- 3. Response time ----------
print("\n" + "=" * 60)
print("3. API RESPONSE TIME (ms), 5 runs per query")
print("=" * 60)

times = []
for q in queries:
    for _ in range(5):
        t = time.perf_counter()
        requests.post(f"{API}/recommend", json={**q, "limit": 10}, timeout=60)
        times.append((time.perf_counter() - t) * 1000)

print(f"/recommend  calls={len(times)}  average={sum(times) / len(times):.0f}  p95={pct(times, 95):.0f}  max={max(times):.0f}")

for name, path, params in [
    ("/filter", "/filter", {"cuisine": "Chinese", "max_budget": 600}),
    ("/compare", "/compare", {"ids": "1,2,3"}),
    ("/dashboard", "/dashboard", {}),
]:
    ts = []
    for _ in range(5):
        t = time.perf_counter()
        requests.get(API + path, params=params, timeout=60)
        ts.append((time.perf_counter() - t) * 1000)
    print(f"{name:<11} calls=5   average={sum(ts) / len(ts):.0f}  max={max(ts):.0f}")

# ---------- 4. Functional tests ----------
print("\n" + "=" * 60)
print("4. FUNCTIONAL AND EDGE-CASE TESTS")
print("=" * 60)

tests = [
    ("Health check", "GET", "/health", {}, 200, None),
    ("Recommend - normal search", "POST", "/recommend", {"json": {"cuisine": "North Indian", "limit": 5}}, 200, None),
    ("Recommend - no match returns empty list", "POST", "/recommend", {"json": {"cuisine": "zzzzzz"}}, 200, "empty"),
    ("Filter - normal", "GET", "/filter", {"params": {"cuisine": "Chinese", "max_budget": 600}}, 200, None),
    ("Filter - min budget above max rejected", "GET", "/filter", {"params": {"min_budget": 1000, "max_budget": 500}}, 400, None),
    ("Compare - valid ids", "GET", "/compare", {"params": {"ids": "1,2,3"}}, 200, None),
    ("Compare - invalid ids rejected", "GET", "/compare", {"params": {"ids": "abc"}}, 400, None),
    ("Compare - unknown ids give 404", "GET", "/compare", {"params": {"ids": "99999999"}}, 404, None),
    ("Dashboard - stats returned", "GET", "/dashboard", {}, 200, None),
]

passed = 0
for name, method, path, kw, expected, special in tests:
    try:
        resp = requests.request(method, API + path, timeout=60, **kw)
        ok = resp.status_code == expected
        if ok and special == "empty":
            ok = resp.json().get("count") == 0
        result = "PASS" if ok else f"FAIL (got {resp.status_code})"
    except Exception as e:
        ok, result = False, f"FAIL ({e})"
    passed += ok
    print(f"{result:<14} {name}")

print(f"\n{passed}/{len(tests)} tests passed")