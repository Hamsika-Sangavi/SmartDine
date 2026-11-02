from fastapi import APIRouter, HTTPException
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from services.ranking import rank_restaurants, haversine_km
from schemas import RecommendRequest

router = APIRouter()

NEARBY_RADIUS_KM = 5

@router.post("/recommend")
def recommend(req: RecommendRequest):
    user_lat, user_lon = req.user_lat, req.user_lon
    use_nearby = bool(req.nearby and req.location)

    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if req.cuisine:
        query += " AND cuisines LIKE %s"
        params.append(f"%{req.cuisine}%")
    if req.location and not use_nearby:
        query += " AND location LIKE %s"
        params.append(f"%{req.location}%")
    if req.veg_only:
        query += " AND is_veg_friendly = TRUE"
    if req.wifi_available:
        query += " AND has_wifi = TRUE"
    if req.parking_available:
        query += " AND has_parking = TRUE"
    if req.wheelchair_accessible:
        query += " AND wheelchair_accessible = TRUE"
    if req.serves_alcohol:
        query += " AND serves_alcohol = TRUE"
    if req.live_music:
        query += " AND live_music = TRUE"
    if req.outdoor_seating:
        query += " AND outdoor_seating = TRUE"
    if req.vegan_options:
        query += " AND has_vegan_options = TRUE"
    if req.halal:
        query += " AND is_halal = TRUE"
    if req.gluten_free:
        query += " AND has_gluten_free = TRUE"

    notes = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if use_nearby:
            cursor.execute(
                "SELECT AVG(latitude) AS lat, AVG(longitude) AS lon FROM restaurants WHERE location LIKE %s",
                (f"%{req.location}%",),
            )
            center = cursor.fetchone()
            if not center or center["lat"] is None:
                cursor.close()
                conn.close()
                return {
                    "count": 0,
                    "results": [],
                    "note": f"Could not find the location '{req.location}' for a nearby search.",
                }
            user_lat, user_lon = float(center["lat"]), float(center["lon"])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while fetching recommendations")

    if use_nearby:
        rows = [
            r for r in rows
            if (d := haversine_km(user_lat, user_lon, r.get("latitude"), r.get("longitude"))) is not None
            and d <= NEARBY_RADIUS_KM
        ]
        notes.append(
            f"Showing restaurants within {NEARBY_RADIUS_KM} km of {req.location}, ranked with distance included. "
            "Distances are approximate (measured from the locality centre)."
        )

    any_amenity = any([req.veg_only, req.wifi_available, req.parking_available, req.wheelchair_accessible,
                        req.serves_alcohol, req.live_music, req.outdoor_seating, req.vegan_options,
                        req.halal, req.gluten_free])
    if any_amenity:
        notes.append(
            "Amenity data is available for about 47% of restaurants, sourced from a secondary dataset; "
            "results are limited to restaurants with confirmed data."
        )

    note = " ".join(notes) if notes else None

    if not rows:
        return {"count": 0, "results": [], "note": note}

    ranked = rank_restaurants(
        rows,
        user_budget=req.budget,
        user_lat=user_lat,
        user_lon=user_lon,
    )

    top = ranked[: req.limit]
    for r in top:
        d = r.pop("_distance_km", None)
        r["distance_km"] = round(d, 1) if d is not None else None

    return {"count": len(top), "results": top, "note": note}