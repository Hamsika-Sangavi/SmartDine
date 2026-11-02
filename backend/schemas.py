from pydantic import BaseModel
from typing import Optional

class RecommendRequest(BaseModel):
    cuisine: Optional[str] = None
    budget: Optional[float] = None
    location: Optional[str] = None
    nearby: Optional[bool] = None
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None
    veg_only: Optional[bool] = None
    wifi_available: Optional[bool] = None
    parking_available: Optional[bool] = None
    wheelchair_accessible: Optional[bool] = None
    serves_alcohol: Optional[bool] = None
    live_music: Optional[bool] = None
    outdoor_seating: Optional[bool] = None
    vegan_options: Optional[bool] = None
    halal: Optional[bool] = None
    gluten_free: Optional[bool] = None
    limit: int = 10

class RestaurantOut(BaseModel):
    id: int
    name: str
    location: str
    rate: Optional[float]
    sentiment_score: Optional[float]
    approx_cost: Optional[float]
    cuisines: Optional[str]
    rest_type: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    sample_review: Optional[str]
    review_summary: Optional[str]
    score: float
    explanation: str