from typing import Dict, List

from app.services.catalog import make_catalog_item


def home_fallback(
    budget: float,
    rooms: List[str],
    style: str,
    items: List[dict],
):
    allocations: Dict[str, float] = {}

    if items:
        total_quantity = sum(
            item.get("quantity", 1)
            for item in items
        )

        for item in items:
            category = item.get(
                "category",
                "Home item",
            )

            quantity = item.get(
                "quantity",
                1,
            )

            share = budget * (
                quantity / total_quantity
            )

            allocations[category] = round(
                share,
                2,
            )
    else:
        allocations = {
            "Furniture": round(
                budget * 0.40,
                2,
            ),
            "Lighting": round(
                budget * 0.20,
                2,
            ),
            "Decor": round(
                budget * 0.15,
                2,
            ),
            "Storage": round(
                budget * 0.15,
                2,
            ),
            "Accessories": round(
                budget * 0.10,
                2,
            ),
        }

    recommendations = [
        make_catalog_item(
            "Modern accent furniture",
            "Furniture",
            "IKEA",
            min(budget * 0.35, 25000),
            f"Works well with a {style} interior.",
            f"{style} accent furniture",
        ),
        make_catalog_item(
            "LED ceiling lighting",
            "Lighting",
            "Amazon",
            min(budget * 0.10, 7000),
            "Budget-friendly lighting upgrade.",
            "LED ceiling light home",
        ),
        make_catalog_item(
            "Decorative wall art",
            "Decor",
            "Amazon",
            min(budget * 0.08, 5000),
            "Adds personality without consuming much of the budget.",
            f"{style} wall decor",
        ),
        make_catalog_item(
            "Compact storage solution",
            "Storage",
            "IKEA",
            min(budget * 0.15, 10000),
            "Useful for keeping the room organized.",
            "home storage furniture",
        ),
        make_catalog_item(
            "Home accessories",
            "Accessories",
            "Flipkart",
            min(budget * 0.08, 5000),
            "Small accessories can complete the room.",
            f"{style} home accessories",
        ),
    ]

    return {
        "planner": "home",
        "budget": budget,
        "summary": (
            f"A {style} home setup can be planned "
            f"within your budget of ₹{budget:,.0f}."
        ),
        "allocations": allocations,
        "recommendations": recommendations,
        "notes": [
            "Prices are indicative search-price targets.",
            "Verify current seller price and availability before purchase.",
        ],
        "source": "fallback",
    }


def party_fallback(
    budget: float,
    guests: int,
    event_type: str,
    venue_type: str,
    city: str | None,
    food_preference: str | None,
    decoration_style: str | None,
):
    catering = budget * 0.45
    venue = budget * 0.20
    decoration = budget * 0.15
    entertainment = budget * 0.10
    contingency = budget * 0.10

    per_guest = catering / guests

    recommendations = [
        make_catalog_item(
            "Catering package",
            "Catering",
            "Swiggy",
            catering,
            (
                f"Approximate catering allocation "
                f"of ₹{catering:,.0f}, or "
                f"₹{per_guest:,.0f} per guest."
            ),
            food_preference or "party catering",
        ),
        make_catalog_item(
            "Restaurant/event food option",
            "Catering",
            "Zomato",
            catering,
            "Useful for comparing nearby food providers.",
            food_preference or "party food",
        ),
        make_catalog_item(
            "Event venue",
            "Venue",
            "OYO",
            venue,
            f"Search options around {city or 'your city'}.",
            f"{event_type} event venue {city or ''}",
        ),
        make_catalog_item(
            "Party decoration",
            "Decoration",
            "Amazon",
            decoration,
            (
                f"{decoration_style or 'simple'} "
                "decor can fit this allocation."
            ),
            f"{event_type} party decoration",
        ),
    ]

    return {
        "planner": "party",
        "budget": budget,
        "summary": (
            f"Your {event_type} for {guests} guests "
            f"can be organized around a ₹{budget:,.0f} budget."
        ),
        "allocations": {
            "Catering": round(catering, 2),
            "Venue": round(venue, 2),
            "Decoration": round(decoration, 2),
            "Entertainment": round(entertainment, 2),
            "Contingency": round(contingency, 2),
        },
        "recommendations": recommendations,
        "notes": [
            "Catering allocation is approximately 45% of the budget.",
            "Keep the contingency amount available for unexpected expenses.",
        ],
        "source": "fallback",
    }


def jewelry_fallback(
    budget: float,
    occasion: str,
    style: str,
    metal: str | None,
    outfit_description: str | None,
    image_analyzed: bool = False,
):
    metal_text = metal or "versatile metal"

    recommendations = [
        make_catalog_item(
            f"{style.title()} earrings",
            "Earrings",
            "Amazon",
            min(budget * 0.20, 8000),
            (
                f"Designed for a {occasion} occasion "
                f"with a {style} preference."
            ),
            f"{style} {metal_text} earrings",
        ),
        make_catalog_item(
            f"{style.title()} necklace",
            "Necklace",
            "Flipkart",
            min(budget * 0.40, 15000),
            "A versatile statement piece for special occasions.",
            f"{style} {metal_text} necklace",
        ),
        make_catalog_item(
            f"{style.title()} bracelet",
            "Bracelet",
            "Amazon",
            min(budget * 0.15, 6000),
            "Works as a complementary accessory.",
            f"{style} {metal_text} bracelet",
        ),
        make_catalog_item(
            f"{style.title()} jewelry set",
            "Set",
            "Flipkart",
            min(budget * 0.50, 18000),
            "Useful when you want coordinated pieces.",
            f"{style} jewelry set",
        ),
    ]

    notes = [
        "Try to match jewelry contrast with the outfit rather than copying its exact color.",
        "Check dimensions, material, return policy and seller reviews before purchase.",
    ]

    if image_analyzed:
        notes.insert(
            0,
            "The uploaded outfit image was received for visual analysis."
        )

    if outfit_description:
        notes.append(
            f"Outfit context considered: {outfit_description}"
        )

    return {
        "planner": "jewelry",
        "budget": budget,
        "summary": (
            f"Here are {style} jewelry ideas for a "
            f"{occasion} occasion within ₹{budget:,.0f}."
        ),
        "allocations": {
            "Earrings": round(budget * 0.20, 2),
            "Necklace": round(budget * 0.40, 2),
            "Bracelet": round(budget * 0.15, 2),
            "Set": round(budget * 0.25, 2),
        },
        "recommendations": recommendations,
        "notes": notes,
        "source": "fallback",
    }