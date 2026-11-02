from fastapi import APIRouter, HTTPException
from typing import Optional
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

router = APIRouter()

@router.get("/filter")
def filter_restaurants(
    cuisine: Optional[str] = None,
    location: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    online_order: Optional[str] = None,
    book_table: Optional[str] = None,
    rest_type: Optional[str] = None,
    veg_only: Optional[bool] = None,
    wifi_available: Optional[bool] = None,
    parking_available: Optional[bool] = None,
    wheelchair_accessible: Optional[bool] = None,
    serves_alcohol: Optional[bool] = None,
    live_music: Optional[bool] = None,
    outdoor_seating: Optional[bool] = None,
    vegan_options: Optional[bool] = None,
    halal: Optional[bool] = None,
    gluten_free: Optional[bool] = None,
    limit: int = 20,
):
    if min_budget is not None and max_budget is not None and min_budget > max_budget:
        raise HTTPException(status_code=400, detail="min_budget cannot be greater than max_budget")

    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if cuisine:
        query += " AND cuisines LIKE %s"
        params.append(f"%{cuisine}%")
    if location:
        query += " AND location LIKE %s"
        params.append(f"%{location}%")
    if min_budget is not None:
        query += " AND approx_cost >= %s"
        params.append(min_budget)
    if max_budget is not None:
        query += " AND approx_cost <= %s"
        params.append(max_budget)
    if online_order:
        query += " AND online_order = %s"
        params.append(online_order)
    if book_table:
        query += " AND book_table = %s"
        params.append(book_table)
    if rest_type:
        query += " AND rest_type LIKE %s"
        params.append(f"%{rest_type}%")
    if veg_only:
        query += " AND is_veg_friendly = TRUE"
    if wifi_available:
        query += " AND has_wifi = TRUE"
    if parking_available:
        query += " AND has_parking = TRUE"
    if wheelchair_accessible:
        query += " AND wheelchair_accessible = TRUE"
    if serves_alcohol:
        query += " AND serves_alcohol = TRUE"
    if live_music:
        query += " AND live_music = TRUE"
    if outdoor_seating:
        query += " AND outdoor_seating = TRUE"
    if vegan_options:
        query += " AND has_vegan_options = TRUE"
    if halal:
        query += " AND is_halal = TRUE"
    if gluten_free:
        query += " AND has_gluten_free = TRUE"

    query += " ORDER BY rate DESC LIMIT %s"
    params.append(limit)

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while filtering restaurants")

    any_amenity = any([veg_only, wifi_available, parking_available, wheelchair_accessible,
                        serves_alcohol, live_music, outdoor_seating, vegan_options, halal, gluten_free])
    note = None
    if any_amenity:
        note = "Amenity data is available for about 47% of restaurants, sourced from a secondary dataset; results are limited to restaurants with confirmed data."

    return {"count": len(rows), "results": rows, "note": note}