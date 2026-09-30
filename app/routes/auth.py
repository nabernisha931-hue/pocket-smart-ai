from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.database import get_db

from app.dependencies import (
    get_current_user
)

from app.models import User

from app.schemas import (
    LoginRequest,
    RegisterRequest,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)


@router.post("/register")
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    email = (
        payload.email
        .lower()
        .strip()
    )

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(
            payload.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response.set_cookie(
        "access_token",
        create_access_token(
            user.id
        ),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7200,
    )

    return {
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    user = db.scalar(
        select(User).where(
            User.email
            == payload.email.lower().strip()
        )
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user.password_hash
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    response.set_cookie(
        "access_token",
        create_access_token(
            user.id
        ),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7200,
    )

    return {
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


@router.post("/logout")
def logout(
    response: Response
):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out."
    }


@router.get("/me")
def me(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }