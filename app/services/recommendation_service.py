import json
import logging

from typing import Any

from PIL import Image

from app.services.catalog_service import (
    catalog_for
)

from app.services.gemini_service import (
    GeminiService
)


logger = logging.getLogger(__name__)


BASE_SYSTEM = """
You are PocketSmart AI, a budget-conscious recommendation assistant.

Return ONLY valid JSON matching the requested schema.

Never invent live prices, availability, ratings, or product IDs.

Treat catalog entries as search suggestions rather than verified inventory.

Respect the user's maximum budget.

Keep recommendations practical, concise, and non-judgmental.
"""


class RecommendationService:

    def __init__(self):

        self.gemini = GeminiService()

    def recommend(
        self,
        planner: str,
        data: dict[str, Any],
        image: Image.Image | None = None,
    ) -> dict[str, Any]:

        catalog = catalog_for(
            planner,
            float(data["budget"]),
            self._query_terms(
                planner,
                data
            ),
        )

        if self.gemini.enabled:

            try:

                return (
                    self._gemini_recommendation(
                        planner,
                        data,
                        catalog,
                        image
                    )
                )

            except Exception as exc:

                logger.exception(
                    "Gemini request failed; using fallback: %s",
                    exc
                )

        return self._fallback(
            planner,
            data,
            catalog,
            image
        )

    def _gemini_recommendation(
        self,
        planner,
        data,
        catalog,
        image
    ):

        prompt = f"""
Planner: {planner}

User data:

{json.dumps(
    data,
    ensure_ascii=False
)}

Candidate catalog:

{json.dumps(
    catalog,
    ensure_ascii=False
)}

Create a balanced plan.

You may select only from the candidate catalog.

Use this JSON shape:

{{
  "summary": "short explanation",

  "allocation": {{
    "category": numeric_amount
  }},

  "recommendations": [

    {{
      "title": "exact candidate title",

      "category": "candidate category",

      "price": numeric_price,

      "platform": "candidate platform",

      "url": "candidate url",

      "reason": "why it fits",

      "budget_share": numeric_percent
    }}

  ],

  "image_insight": "optional outfit insight or null"
}}

The sum of allocation values must be <= the user's budget.

Return at most 8 recommendations.
"""

        result = self.gemini.generate(
            BASE_SYSTEM,
            prompt,
            image=image
        )

        return self._normalize(
            result,
            planner,
            float(data["budget"])
        )

    def _normalize(
        self,
        result,
        planner,
        budget
    ):

        result["allocation"] = {

            str(k):
                max(
                    0.0,
                    float(v)
                )

            for k, v in (
                result.get(
                    "allocation"
                ) or {}
            ).items()
        }

        result["recommendations"] = (
            result.get(
                "recommendations"
            ) or []
        )

        for item in result[
            "recommendations"
        ]:

            item["price"] = float(
                item.get(
                    "price",
                    0
                )
            )

            item["budget_share"] = float(
                item.get(
                    "budget_share",
                    0
                )
            )

        result["planner"] = planner

        result["budget"] = budget

        result["source"] = "gemini"

        result.setdefault(
            "image_insight",
            None
        )

        return result

    def _fallback(
        self,
        planner,
        data,
        catalog,
        image
    ):

        budget = float(
            data["budget"]
        )

        if planner == "home":

            allocation = {

                "Furniture":
                    round(
                        budget * 0.45,
                        2
                    ),

                "Lighting":
                    round(
                        budget * 0.20,
                        2
                    ),

                "Decor":
                    round(
                        budget * 0.20,
                        2
                    ),

                "Buffer":
                    round(
                        budget * 0.15,
                        2
                    ),
            }

            summary = (
                f"A practical "
                f"{data['style']} "
                f"{data['room']} plan "
                f"for a budget of "
                f"₹{budget:,.0f}. "
                f"The 15% buffer helps "
                f"cover delivery or "
                f"unexpected costs."
            )

        elif planner == "party":

            allocation = {

                "Food":
                    round(
                        budget * 0.45,
                        2
                    ),

                "Decoration":
                    round(
                        budget * 0.20,
                        2
                    ),

                "Accommodation":
                    round(
                        budget * 0.20,
                        2
                    ),

                "Buffer":
                    round(
                        budget * 0.15,
                        2
                    ),
            }

            summary = (
                f"A balanced "
                f"{data['event_type']} "
                f"plan for "
                f"{data['guests']} guests "
                f"within "
                f"₹{budget:,.0f}."
            )

        else:

            allocation = {

                "Main jewelry":
                    round(
                        budget * 0.60,
                        2
                    ),

                "Secondary piece":
                    round(
                        budget * 0.25,
                        2
                    ),

                "Buffer":
                    round(
                        budget * 0.15,
                        2
                    ),
            }

            summary = (
                f"A {data['style']} "
                f"jewelry plan for a "
                f"{data['occasion']} "
                f"within "
                f"₹{budget:,.0f}. "
                f"The image is treated "
                f"as optional style context."
            )

        chosen = [
            x
            for x in catalog
            if x["price"] <= budget
        ][:6]

        recommendations = []

        for item in chosen:

            recommendations.append(
                {
                    "title":
                        item["title"],

                    "category":
                        item["category"],

                    "price":
                        item["price"],

                    "platform":
                        item["platform"],

                    "url":
                        item["url"],

                    "reason":
                        self._reason(
                            planner,
                            data,
                            item
                        ),

                    "budget_share":
                        round(
                            item["price"]
                            / budget
                            * 100,
                            2
                        ),
                }
            )

        if (
            image is not None
            and planner == "jewelry"
        ):

            image_insight = (
                "Outfit image received. "
                "The fallback engine cannot "
                "perform visual analysis, so "
                "recommendations are based on "
                "the text preferences."
            )

        else:

            image_insight = None

        return {

            "planner":
                planner,

            "budget":
                budget,

            "summary":
                summary,

            "allocation":
                allocation,

            "recommendations":
                recommendations,

            "source":
                "fallback",

            "image_insight":
                image_insight,
        }

    @staticmethod
    def _query_terms(
        planner,
        data
    ):

        if planner == "home":

            return [
                data.get(
                    "room",
                    ""
                ),

                data.get(
                    "style",
                    ""
                ),

                *data.get(
                    "items",
                    []
                ),
            ]

        if planner == "party":

            return [
                data.get(
                    "event_type",
                    ""
                ),

                data.get(
                    "food_preference",
                    ""
                ),
            ]

        return [
            data.get(
                "occasion",
                ""
            ),

            data.get(
                "style",
                ""
            ),

            data.get(
                "metal",
                ""
            ),
        ]

    @staticmethod
    def _reason(
        planner,
        data,
        item
    ):

        if planner == "home":

            return (
                f"Fits the "
                f"{data['style']} "
                f"style and is "
                f"within the planner budget."
            )

        if planner == "party":

            return (
                f"Useful for a "
                f"{data['event_type']} "
                f"with "
                f"{data['guests']} guests."
            )

        return (
            f"Matches the "
            f"{data['occasion']} "
            f"occasion and "
            f"{data['style']} "
            f"preference."
        )