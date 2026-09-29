import json

from fastapi import (
    APIRouter,
    File,
    Form,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import get_conn
from app.models.schemas import (
    HomeRequest,
    PartyRequest,
    JewelryRequest,
)
from app.services.auth import decode_access_token
from app.services.recommendations import (
    generate_home,
    generate_jewelry,
    generate_party,
)


router = APIRouter(
    prefix="/api",
    tags=["Planners"],
)

settings = get_settings()


def get_current_user_id(
    request: Request,
):
    token = request.cookies.get(
        "pocketsmart_token"
    )

    if not token:
        return None

    return decode_access_token(token)


def save_recommendation(
    user_id: int,
    planner: str,
    budget: float,
    request_data: dict,
    response_data: dict,
):
    conn = get_conn()

    try:
        conn.execute(
            """
            INSERT INTO recommendations
            (
                user_id,
                planner,
                budget,
                request_json,
                response_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                planner,
                budget,
                json.dumps(
                    request_data,
                    default=str,
                ),
                json.dumps(
                    response_data,
                    default=str,
                ),
            ),
        )

        conn.commit()

    finally:
        conn.close()


@router.post("/generate-home")
async def generate_home_api(
    request: Request,
    payload: HomeRequest,
):
    result = generate_home(
        payload.model_dump()
    )

    user_id = get_current_user_id(
        request
    )

    if user_id:
        save_recommendation(
            user_id=user_id,
            planner="home",
            budget=payload.budget,
            request_data=payload.model_dump(),
            response_data=result,
        )

    return result


@router.post("/generate-party")
async def generate_party_api(
    request: Request,
    payload: PartyRequest,
):
    result = generate_party(
        payload.model_dump()
    )

    user_id = get_current_user_id(
        request
    )

    if user_id:
        save_recommendation(
            user_id=user_id,
            planner="party",
            budget=payload.budget,
            request_data=payload.model_dump(),
            response_data=result,
        )

    return result


@router.post("/generate-jewelry")
async def generate_jewelry_api(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form("party"),
    style: str = Form("elegant"),
    metal: str = Form(""),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
):
    image_bytes = None
    image_mime_type = None

    if outfit_image and outfit_image.filename:
        max_bytes = (
            settings.max_upload_mb
            * 1024
            * 1024
        )

        image_bytes = await outfit_image.read()

        if len(image_bytes) > max_bytes:
            return JSONResponse(
                {
                    "success": False,
                    "message": (
                        f"Image must be smaller than "
                        f"{settings.max_upload_mb} MB."
                    ),
                },
                status_code=413,
            )

        image_mime_type = (
            outfit_image.content_type
            or "image/jpeg"
        )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if image_mime_type not in allowed_types:
            return JSONResponse(
                {
                    "success": False,
                    "message": (
                        "Only JPG, PNG and WebP "
                        "images are supported."
                    ),
                },
                status_code=400,
            )

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        metal=metal or None,
        outfit_description=(
            outfit_description or None
        ),
    )

    request_data = payload.model_dump()

    result = generate_jewelry(
        request_data,
        image_bytes=image_bytes,
        image_mime_type=image_mime_type,
    )

    user_id = get_current_user_id(
        request
    )

    if user_id:
        save_recommendation(
            user_id=user_id,
            planner="jewelry",
            budget=budget,
            request_data=request_data,
            response_data=result,
        )

    return result