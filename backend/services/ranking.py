import math

WEIGHTS = {
    "rating": 0.4,
    "sentiment": 0.3,
    "budget": 0.2,
    "distance": 0.1,
}

NON_VEG_KEYWORDS = ["chicken", "mutton", "fish", "beef", "pork", "prawn", "egg", "seafood", "meat"]

def is_vegetarian_friendly(cuisines: str) -> bool:
    if not cuisines:
        return False
    lower = cuisines.lower()
    return not any(word in lower for word in NON_VEG_KEYWORDS)

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

def haversine_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

def budget_fit_score(approx_cost, user_budget):
    if approx_cost is None or user_budget is None:
        return 0.5
    diff = abs(approx_cost - user_budget)
    return max(0, 1 - (diff / max(user_budget, 1)))

def rank_restaurants(restaurants, user_budget=None, user_lat=None, user_lon=None):
    ratings = [r["rate"] for r in restaurants if r["rate"] is not None]
    min_rate, max_rate = (min(ratings), max(ratings)) if ratings else (0, 5)

    sentiments = [r["sentiment_score"] for r in restaurants if r["sentiment_score"] is not None]
    min_sent, max_sent = (min(sentiments), max(sentiments)) if sentiments else (-1, 1)

    distances = []
    for r in restaurants:
        d = haversine_km(user_lat, user_lon, r.get("latitude"), r.get("longitude"))
        r["_distance_km"] = d
        if d is not None:
            distances.append(d)
    min_dist, max_dist = (min(distances), max(distances)) if distances else (0, 1)

    for r in restaurants:
        rate_score = normalize(r["rate"], min_rate, max_rate) if r["rate"] is not None else 0.5
        sent_score = normalize(r["sentiment_score"], min_sent, max_sent) if r["sentiment_score"] is not None else 0.5
        budget_score = budget_fit_score(r.get("approx_cost"), user_budget)
        if r["_distance_km"] is not None and max_dist > min_dist:
            dist_score = 1 - normalize(r["_distance_km"], min_dist, max_dist)
        else:
            dist_score = 0.5

        score = (
            WEIGHTS["rating"] * rate_score +
            WEIGHTS["sentiment"] * sent_score +
            WEIGHTS["budget"] * budget_score +
            WEIGHTS["distance"] * dist_score
        )
        r["score"] = round(score, 4)

        reasons = []
        if rate_score > 0.7:
            reasons.append("highly rated")
        if sent_score > 0.7:
            reasons.append("very positive reviews")
        if budget_score > 0.8:
            reasons.append("fits your budget")
        if r["_distance_km"] is not None and r["_distance_km"] < 3:
            reasons.append("close to you")
        r["explanation"] = ", ".join(reasons) if reasons else "balanced match across rating, reviews, and budget"

    return sorted(restaurants, key=lambda x: x["score"], reverse=True)