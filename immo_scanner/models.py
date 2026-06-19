from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SearchCriteria:
    cities: list[str] = field(default_factory=list)
    departments: list[str] = field(default_factory=list)
    radius_km: int = 20
    budget_min: int = 0
    budget_max: int = 500000
    surface_min: int = 0
    surface_max: Optional[int] = None
    property_types: list[str] = field(default_factory=lambda: ["apartment", "house", "building"])
    rooms_min: Optional[int] = None
    rooms_max: Optional[int] = None
    max_pages: int = 5
    transaction_type: str = "buy"


@dataclass
class Property:
    title: str
    price: int
    city: str
    postal_code: str = ""
    address: str = ""
    surface: float = 0.0
    rooms: Optional[int] = None
    property_type: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    image_url: str = ""
    floor: Optional[int] = None
    year_built: Optional[int] = None
    dpe: str = ""
    charges: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date_posted: Optional[datetime] = None
    raw_data: dict = field(default_factory=dict)

    @property
    def price_per_sqm(self) -> float:
        if self.surface and self.surface > 0:
            return self.price / self.surface
        return 0.0

    def dedup_key(self) -> str:
        parts = [
            self.city.lower().strip(),
            str(int(self.surface)) if self.surface else "",
            str(self.price),
        ]
        if self.latitude and self.longitude:
            parts.extend([f"{self.latitude:.4f}", f"{self.longitude:.4f}"])
        return "|".join(parts)


@dataclass
class RentalEstimate:
    monthly_rent: float
    source: str
    confidence: str = "medium"
    rent_per_sqm: float = 0.0


@dataclass
class ScoredProperty:
    property: Property
    rental_estimate: Optional[RentalEstimate] = None
    gross_yield: float = 0.0
    net_yield: float = 0.0
    score: float = 0.0
    score_details: dict = field(default_factory=dict)

    @property
    def monthly_rent(self) -> float:
        return self.rental_estimate.monthly_rent if self.rental_estimate else 0.0
