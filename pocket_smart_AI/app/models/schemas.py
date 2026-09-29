from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class HomeItem(BaseModel):
    category: str
    quantity: int = Field(default=1, ge=1, le=100)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: List[str] = Field(default_factory=list)
    style: str = "modern"
    items: List[HomeItem] = Field(default_factory=list)
    city: Optional[str] = None


class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = "birthday"
    venue_type: str = "home"
    city: Optional[str] = None
    food_preference: Optional[str] = None
    decoration_style: Optional[str] = None


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0)
    occasion: str = "party"
    style: str = "elegant"
    metal: Optional[str] = None
    outfit_description: Optional[str] = None


class RecommendationItem(BaseModel):
    title: str
    category: str
    platform: str
    price: float
    reason: str
    url: str


class RecommendationResponse(BaseModel):
    planner: str
    budget: float
    summary: str
    allocations: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    source: str = "fallback"
    raw: Optional[Dict[str, Any]] = None