import json

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies import (
    get_current_user
)

from app.models import (
    RecommendationHistory,
    User,
)


router = APIRouter(
    prefix="/api",
    tags=["history"]
)


@router.get("/history")
def history(
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    rows = db.scalars(
        select(
            RecommendationHistory
        )
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(limit)
    ).all()

    return [
        {
            "id": row.id,

            "planner_type":
                row.planner_type,

            "created_at":
                row.created_at.isoformat(),

            "input":
                json.loads(
                    row.input_json
                ),

            "result":
                json.loads(
                    row.result_json
                ),
        }

        for row in rows
    ]


@router.get("/session-info")
def session_info(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "authenticated": True,
        "user_id": user.id,
        "name": user.name,
    }


@router.get("/session-data")
def session_data(
    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    count = (
        db.query(
            RecommendationHistory
        )
        .filter(
            RecommendationHistory.user_id
            == user.id
        )
        .count()
    )

    return {
        "user_id": user.id,
        "recommendation_count": count,
    }