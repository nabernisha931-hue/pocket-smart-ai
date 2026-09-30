import json
import logging

from typing import Any

from PIL import Image

from google import genai

from google.genai import types

from app.config import get_settings


logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self):

        self.settings = get_settings()

        self.client = (

            genai.Client(
                api_key=
                self.settings.gemini_api_key
            )

            if self.settings.gemini_api_key

            else None
        )

    @property
    def enabled(self) -> bool:

        return self.client is not None

    def generate(
        self,
        system_instruction: str,
        prompt: str,
        image: Image.Image | None = None,
    ) -> dict[str, Any]:

        if not self.client:

            raise RuntimeError(
                "Gemini API is not configured."
            )

        contents: list[Any] = [
            prompt
        ]

        if image is not None:

            contents.append(
                image
            )

        response = (
            self.client.models.generate_content(
                model=self.settings.gemini_model,

                contents=contents,

                config=types.GenerateContentConfig(
                    system_instruction=
                        system_instruction,

                    temperature=0.4,

                    response_mime_type="application/json",
                ),
            )
        )

        raw = response.text or ""

        return self._parse_json(
            raw
        )

    @staticmethod
    def _parse_json(
        raw: str
    ) -> dict[str, Any]:

        cleaned = raw.strip()

        if cleaned.startswith("```"):

            cleaned = (
                cleaned
                .replace(
                    "```json",
                    "",
                    1
                )
                .replace(
                    "```",
                    "",
                    1
                )
                .strip()
            )

        try:

            value = json.loads(
                cleaned
            )

        except json.JSONDecodeError as exc:

            logger.warning(
                "Gemini returned non-JSON output: %s",
                raw[:500]
            )

            raise ValueError(
                "Gemini returned an invalid JSON response."
            ) from exc

        if not isinstance(
            value,
            dict
        ):

            raise ValueError(
                "Gemini response must be a JSON object."
            )

        return value