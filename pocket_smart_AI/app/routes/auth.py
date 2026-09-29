from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_id,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def _current_user(request: Request):
    token = request.cookies.get(
        "pocketsmart_token"
    )

    if not token:
        return None

    from app.services.auth import decode_access_token

    user_id = decode_access_token(token)

    if not user_id:
        return None

    return get_user_by_id(user_id)


@router.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    user = create_user(
        name=name,
        email=email,
        password=password,
    )

    if not user:
        return JSONResponse(
            {
                "success": False,
                "message": "Email already registered.",
            },
            status_code=409,
        )

    token = create_access_token(
        user["id"]
    )

    response = JSONResponse(
        {
            "success": True,
            "message": "Registration successful.",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
        }
    )

    response.set_cookie(
        "pocketsmart_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )

    return response


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
):
    user = authenticate_user(
        email,
        password,
    )

    if not user:
        return JSONResponse(
            {
                "success": False,
                "message": "Invalid email or password.",
            },
            status_code=401,
        )

    token = create_access_token(
        user["id"]
    )

    response = JSONResponse(
        {
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
        }
    )

    response.set_cookie(
        "pocketsmart_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )

    return response


@router.post("/logout")
async def logout():
    response = JSONResponse(
        {
            "success": True,
            "message": "Logged out successfully.",
        }
    )

    response.delete_cookie(
        "pocketsmart_token"
    )

    return response


@router.get("/session-info")
async def session_info(
    request: Request,
):
    user = _current_user(request)

    if not user:
        return {
            "authenticated": False,
            "user": None,
        }

    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


@router.get("/session-data")
async def session_data(
    request: Request,
):
    user = _current_user(request)

    if not user:
        return JSONResponse(
            {
                "authenticated": False,
                "message": "Login required.",
            },
            status_code=401,
        )

    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }