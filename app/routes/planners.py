import json

from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from PIL import (
    Image,
    UnidentifiedImageError,
)

from sqlalchemy.orm import Session

from app.config import get_settings

from app.database import get_db

from app.dependencies import (
    get_current_user
)

from app.models import (
    RecommendationHistory,
    User,
)

from app.recommendation_models import (
    validate_result
)

from app.schemas import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
)

from app.services.recommendation_service import (
    RecommendationService
)


router = APIRouter(
    prefix="/api",
    tags=["planners"]
)


service = RecommendationService()


def save_history(
    db,
    user,
    planner,
    payload,
    result
):

    row = RecommendationHistory(

        user_id=user.id,

        planner_type=planner,

        input_json=json.dumps(
            payload,
            ensure_ascii=False
        ),

        result_json=json.dumps(
            result,
            ensure_ascii=False
        ),
    )

    db.add(row)

    db.commit()


@router.post(
    "/generate-home"
)
def generate_home(
    payload: HomeRequest,

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    result = service.recommend(
        "home",
        payload.model_dump()
    )

    result = validate_result(
        result
    )

    save_history(
        db,
        user,
        "home",
        payload.model_dump(),
        result
    )

    return result


@router.post(
    "/generate-party"
)
def generate_party(
    payload: PartyRequest,

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    result = service.recommend(
        "party",
        payload.model_dump()
    )

    result = validate_result(
        result
    )

    save_history(
        db,
        user,
        "party",
        payload.model_dump(),
        result
    )

    return result


@router.post(
    "/generate-jewelry"
)
async def generate_jewelry(

    budget: float = Form(...),

    occasion: str = Form(...),

    style: str = Form(...),

    metal: str = Form("Any"),

    outfit_notes: str = Form(""),

    outfit_image: UploadFile | None =
        File(default=None),

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    if (
        budget <= 0
        or budget > 100_000_000
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Budget must be greater than 0."
            ),
        )

    image = None

    if (
        outfit_image
        and outfit_image.filename
    ):

        settings = get_settings()

        if (
            not outfit_image.content_type
            or not outfit_image.content_type.startswith(
                "image/"
            )
        ):

            raise HTTPException(
                status_code=415,
                detail=(
                    "Only image uploads "
                    "are accepted."
                ),
            )

        raw = await outfit_image.read()

        if (
            len(raw)
            > settings.max_upload_mb
            * 1024
            * 1024
        ):

            raise HTTPException(
                status_code=413,
                detail=(
                    "Image is too large."
                ),
            )

        try:

            image = (
                Image
                .open(
                    BytesIO(raw)
                )
                .convert("RGB")
            )

        except UnidentifiedImageError:

            raise HTTPException(
                status_code=415,
                detail=(
                    "The uploaded file "
                    "is not a valid image."
                ),
            )

    payload = JewelryRequest(

        budget=budget,

        occasion=occasion,

        style=style,

        metal=metal,

        outfit_notes=outfit_notes,
    )

    result = service.recommend(
        "jewelry",
        payload.model_dump(),
        image=image
    )

    result = validate_result(
        result
    )

    save_history(
        db,
        user,
        "jewelry",
        payload.model_dump(),
        result
    )

    return result