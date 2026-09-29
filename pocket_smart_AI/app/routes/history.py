import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.db import get_conn
from app.services.auth import decode_access_token


router = APIRouter(
    prefix="/api",
    tags=["History"],
)


def current_user_id(request: Request):
    token = request.cookies.get(
        "pocketsmart_token"
    )

    if not token:
        return None

    return decode_access_token(token)


@router.get("/history")
async def history(
    request: Request,
):
    user_id = current_user_id(request)

    if not user_id:
        return JSONResponse(
            {
                "success": False,
                "message": "Login required.",
            },
            status_code=401,
        )

    conn = get_conn()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                planner,
                budget,
                request_json,
                response_json,
                created_at
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

        results = []

        for row in rows:
            results.append(
                {
                    "id": row["id"],
                    "planner": row["planner"],
                    "budget": row["budget"],
                    "request": json.loads(
                        row["request_json"]
                    ),
                    "response": json.loads(
                        row["response_json"]
                    ),
                    "created_at": row["created_at"],
                }
            )

        return {
            "success": True,
            "history": results,
        }

    finally:
        conn.close()