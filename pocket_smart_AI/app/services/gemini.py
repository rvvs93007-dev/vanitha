import base64
import json
from typing import Any, Dict, Optional

from app.config import get_settings


settings = get_settings()


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end > start:
            return json.loads(
                text[start:end + 1]
            )

        raise


def _client():
    if not settings.gemini_api_key:
        return None

    try:
        from google import genai

        return genai.Client(
            api_key=settings.gemini_api_key
        )

    except Exception:
        return None


def _schema_instruction():
    return """
Return ONLY valid JSON.

Use exactly this structure:

{
  "summary": "string",
  "allocations": {
    "category": number
  },
  "recommendations": [
    {
      "title": "string",
      "category": "string",
      "platform": "Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO",
      "price": number,
      "reason": "string",
      "url": "string"
    }
  ],
  "notes": ["string"]
}

Do not return markdown.
Do not return JSON inside another object.
Prices must be numeric.
"""


def generate_with_gemini(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = None,
):
    client = _client()

    if client is None:
        return None

    try:
        from google.genai import types

        contents = [prompt]

        if image_bytes:
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=image_mime_type
                or "image/jpeg",
            )

            contents.append(image_part)

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            return None

        result = _extract_json(text)

        result["_raw_text"] = text

        return result

    except Exception:
        return None


def build_home_prompt(data: Dict[str, Any]) -> str:
    return f"""
You are PocketSmart AI's home interior recommendation engine.

User budget:
₹{data["budget"]}

Rooms:
{json.dumps(data.get("rooms", []))}

Interior style:
{data.get("style", "modern")}

Requested items:
{json.dumps(data.get("items", []))}

City:
{data.get("city") or "Not provided"}

Create practical recommendations that stay within the budget.

Use platforms such as Amazon, IKEA and Flipkart.

Important:
- Do not claim live inventory.
- Treat prices as approximate.
- Keep the total recommendation plan within budget.
- Explain why each item fits the requested style.
- Prefer multiple categories rather than spending everything on one item.

{_schema_instruction()}
"""


def build_party_prompt(data: Dict[str, Any]) -> str:
    return f"""
You are PocketSmart AI's party planning recommendation engine.

Total budget:
₹{data["budget"]}

Guests:
{data["guests"]}

Event type:
{data["event_type"]}

Venue type:
{data["venue_type"]}

City:
{data.get("city") or "Not provided"}

Food preference:
{data.get("food_preference") or "Not provided"}

Decoration style:
{data.get("decoration_style") or "Not provided"}

Allocate the budget across:
- catering
- venue
- decoration
- entertainment
- contingency

Recommend useful options using platforms such as Swiggy, Zomato,
OYO and Amazon.

Do not claim live availability.

{_schema_instruction()}
"""


def build_jewelry_prompt(
    data: Dict[str, Any],
    image_present: bool = False,
) -> str:
    return f"""
You are PocketSmart AI's jewelry recommendation engine.

Budget:
₹{data["budget"]}

Occasion:
{data["occasion"]}

Style:
{data["style"]}

Preferred metal:
{data.get("metal") or "Not specified"}

Outfit description:
{data.get("outfit_description") or "Not provided"}

An outfit image is {'attached' if image_present else 'not attached'}.

If an image is attached:
- analyze dominant outfit colors
- identify broad style/formality
- recommend complementary jewelry
- do not infer sensitive personal attributes

Use Amazon and Flipkart for product searches.

Keep recommendations within budget.

{_schema_instruction()}
"""