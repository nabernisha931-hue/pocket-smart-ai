from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


PlannerType = Literal[
    "home",
    "party",
    "jewelry"
]


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=100_000_000
    )

    room: str = Field(
        min_length=2,
        max_length=80
    )

    style: str = Field(
        min_length=2,
        max_length=80
    )

    occupants: int = Field(
        default=1,
        ge=1,
        le=50
    )

    items: list[str] = Field(
        default_factory=list,
        max_length=30
    )

    priorities: list[str] = Field(
        default_factory=list,
        max_length=10
    )


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=100_000_000
    )

    guests: int = Field(
        gt=0,
        le=100_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=80
    )

    venue: str = Field(
        default="Flexible",
        max_length=120
    )

    food_preference: str = Field(
        default="Mixed",
        max_length=80
    )

    city: str = Field(
        default="India",
        max_length=120
    )


class JewelryRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=100_000_000
    )

    occasion: str = Field(
        min_length=2,
        max_length=80
    )

    style: str = Field(
        min_length=2,
        max_length=80
    )

    metal: str = Field(
        default="Any",
        max_length=80
    )

    outfit_notes: str = Field(
        default="",
        max_length=1000
    )


class RecommendationItem(BaseModel):

    title: str

    category: str

    price: float

    platform: str

    url: str

    reason: str

    budget_share: float = Field(
        ge=0,
        le=100
    )


class RecommendationResponse(BaseModel):

    planner: PlannerType

    budget: float

    summary: str

    allocation: dict[str, float]

    recommendations: list[
        RecommendationItem
    ]

    source: Literal[
        "gemini",
        "fallback"
    ]

    image_insight: str | None = None

    model_config = ConfigDict(
        extra="ignore"
    )


class HistoryItem(BaseModel):

    id: int

    planner_type: PlannerType

    created_at: str

    input: dict

    result: dict