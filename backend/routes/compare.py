from fastapi import APIRouter, HTTPException
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

router = APIRouter()

@router.get("/compare")
def compare_restaurants(ids: str):
    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]

    if not id_list:
        raise HTTPException(status_code=400, detail="Provide valid restaurant IDs, e.g. ?ids=1,2,3")
    if len(id_list) > 5:
        raise HTTPException(status_code=400, detail="Compare up to 5 restaurants at a time")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        placeholders = ",".join(["%s"] * len(id_list))
        query = f"SELECT * FROM restaurants WHERE id IN ({placeholders})"
        cursor.execute(query, id_list)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception:
        raise HTTPException(status_code=500, detail="Database error while comparing restaurants")

    if not rows:
        raise HTTPException(status_code=404, detail="No restaurants found for the given IDs")

    return {"count": len(rows), "results": rows}