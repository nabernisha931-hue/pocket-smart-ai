from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import (
    JWTError,
    jwt,
)

from passlib.context import CryptContext

from fastapi import (
    HTTPException,
    status,
)

from app.config import get_settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain: str,
    hashed: str
) -> bool:

    return pwd_context.verify(
        plain,
        hashed
    )


def create_access_token(
    user_id: int
) -> str:

    settings = get_settings()

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str
) -> int:

    settings = get_settings()

    try:

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm
            ],
        )

        subject = payload.get("sub")

        if not subject:
            raise ValueError

        return int(subject)

    except (
        JWTError,
        ValueError
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )