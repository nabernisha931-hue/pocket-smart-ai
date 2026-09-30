from app.schemas import RecommendationResponse


def validate_result(
    result: dict
) -> dict:

    validated = (
        RecommendationResponse
        .model_validate(result)
    )

    return validated.model_dump()