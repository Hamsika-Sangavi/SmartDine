from fastapi import APIRouter
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

router = APIRouter()

@router.get("/dashboard")
def dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT location, COUNT(*) as count, AVG(rate) as avg_rating
        FROM restaurants GROUP BY location ORDER BY count DESC LIMIT 10
    """)
    by_location = cursor.fetchall()

    cursor.execute("""
        SELECT rest_type, COUNT(*) as count
        FROM restaurants GROUP BY rest_type ORDER BY count DESC LIMIT 10
    """)
    by_type = cursor.fetchall()

    cursor.execute("SELECT AVG(rate) as avg_rating, AVG(sentiment_score) as avg_sentiment FROM restaurants")
    overall = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "by_location": by_location,
        "by_rest_type": by_type,
        "overall": overall,
    }