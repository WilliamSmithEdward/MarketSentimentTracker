# openai_client.py

import json
import os
from typing import Any

from openai import OpenAI

DEFAULT_MODEL = "gpt-5.4"


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=api_key)


def generate_text(prompt: str, model: str = DEFAULT_MODEL) -> str:
    client = get_client()

    response = client.responses.create(
        model=model,
        input=prompt
    )

    return response.output_text


def generate_json(prompt: str, schema: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, Any]:
    client = get_client()

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Return only valid JSON. "
                            "Do not include markdown, code fences, or extra text. "
                            "The response must strictly match the provided JSON schema."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "structured_output",
                "schema": schema,
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)
