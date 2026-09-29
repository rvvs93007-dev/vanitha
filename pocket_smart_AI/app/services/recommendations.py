from typing import Any, Dict, Optional

from app.services.fallback import (
    home_fallback,
    jewelry_fallback,
    party_fallback,
)
from app.services.gemini import (
    build_home_prompt,
    build_jewelry_prompt,
    build_party_prompt,
    generate_with_gemini,
)


def _normalise_ai_result(
    planner: str,
    budget: float,
    ai_result: Dict[str, Any],
):
    recommendations = []

    for item in ai_result.get(
        "recommendations",
        [],
    ):
        try:
            recommendations.append(
                {
                    "title": str(
                        item.get(
                            "title",
                            "Recommendation",
                        )
                    ),
                    "category": str(
                        item.get(
                            "category",
                            "General",
                        )
                    ),
                    "platform": str(
                        item.get(
                            "platform",
                            "Amazon",
                        )
                    ),
                    "price": float(
                        item.get(
                            "price",
                            0,
                        )
                    ),
                    "reason": str(
                        item.get(
                            "reason",
                            "",
                        )
                    ),
                    "url": str(
                        item.get(
                            "url",
                            "",
                        )
                    ),
                }
            )
        except (ValueError, TypeError):
            continue

    return {
        "planner": planner,
        "budget": budget,
        "summary": ai_result.get(
            "summary",
            "AI-generated recommendations.",
        ),
        "allocations": ai_result.get(
            "allocations",
            {},
        ),
        "recommendations": recommendations,
        "notes": ai_result.get(
            "notes",
            [],
        ),
        "source": "gemini",
        "raw": ai_result,
    }


def generate_home(data: Dict[str, Any]):
    ai = generate_with_gemini(
        build_home_prompt(data)
    )

    if ai:
        return _normalise_ai_result(
            "home",
            data["budget"],
            ai,
        )

    return home_fallback(
        budget=data["budget"],
        rooms=data.get("rooms", []),
        style=data.get("style", "modern"),
        items=data.get("items", []),
    )


def generate_party(data: Dict[str, Any]):
    ai = generate_with_gemini(
        build_party_prompt(data)
    )

    if ai:
        return _normalise_ai_result(
            "party",
            data["budget"],
            ai,
        )

    return party_fallback(
        budget=data["budget"],
        guests=data["guests"],
        event_type=data.get(
            "event_type",
            "birthday",
        ),
        venue_type=data.get(
            "venue_type",
            "home",
        ),
        city=data.get("city"),
        food_preference=data.get(
            "food_preference"
        ),
        decoration_style=data.get(
            "decoration_style"
        ),
    )


def generate_jewelry(
    data: Dict[str, Any],
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = None,
):
    ai = generate_with_gemini(
        build_jewelry_prompt(
            data,
            image_present=bool(image_bytes),
        ),
        image_bytes=image_bytes,
        image_mime_type=image_mime_type,
    )

    if ai:
        return _normalise_ai_result(
            "jewelry",
            data["budget"],
            ai,
        )

    return jewelry_fallback(
        budget=data["budget"],
        occasion=data.get(
            "occasion",
            "party",
        ),
        style=data.get(
            "style",
            "elegant",
        ),
        metal=data.get("metal"),
        outfit_description=data.get(
            "outfit_description"
        ),
        image_analyzed=bool(image_bytes),
    )