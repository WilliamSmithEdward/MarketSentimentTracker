# main.py

from datetime import datetime
import json
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

from openai_client import generate_json
from web_scraper import get_json

from market_report_html import render_market_report_html

from html_to_pdf import html_file_to_pdf, html_string_to_pdf

load_dotenv()

ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "djia": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "bias_1d": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down", "neutral"]},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["direction", "confidence", "rationale"]
                },
                "bias_5d": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down", "neutral"]},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["direction", "confidence", "rationale"]
                }
            },
            "required": ["bias_1d", "bias_5d"]
        },
        "sp500": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "bias_1d": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down", "neutral"]},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["direction", "confidence", "rationale"]
                },
                "bias_5d": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down", "neutral"]},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["direction", "confidence", "rationale"]
                }
            },
            "required": ["bias_1d", "bias_5d"]
        },
        "key_drivers": {
            "type": "array",
            "items": {"type": "string"}
        },
        "counterarguments": {
            "type": "array",
            "items": {"type": "string"}
        },
        "what_would_change_view": {
            "type": "array",
            "items": {"type": "string"}
        },
        "eli5_summary": {"type": "string"},
        "eli12_summary": {"type": "string"},
        "eli18_summary": {"type": "string"},
        "eli40_summary": {"type": "string"},
        "long_position_recommendation": {"type": "string"},
        "market_reentry_recommendation": {"type": "string"},
        "sentiment_score": {"type": "integer", "minimum": 1, "maximum": 10},
        "final_vibe_summary": {"type": "string"}
    },
    "required": [
        "djia",
        "sp500",
        "key_drivers",
        "counterarguments",
        "what_would_change_view",
        "eli5_summary",
        "eli12_summary",
        "eli18_summary",
        "eli40_summary",
        "long_position_recommendation",
        "market_reentry_recommendation",
        "sentiment_score",
        "final_vibe_summary"
    ]
}


def get_openai_json(prompt: str) -> dict:
    return generate_json(
        prompt=prompt,
        schema=ANALYSIS_SCHEMA,
        model="gpt-5.4"
    )


def get_news_json(keywords: list[str]) -> list[dict]:
    api_key = os.environ["NEWS_API_KEY"]
    results: list[dict] = []

    for keyword in keywords:
        url = ( 
            "https://newsapi.org/v2/top-headlines"
            f"?country=us&category=business&q={quote_plus(keyword)}&apiKey={api_key}"
        )
        results.append(get_json(url))

    return results


def main() -> None:
    keywords = ["stock", "economy", "iran", "oil", "futures"]
    news_json = get_news_json(keywords)

    analysis = get_openai_json(
        f"""
        You are a market analysis engine.

        Task:
        Analyze the following news JSON and estimate near-term directional bias for:
        - DJIA
        - S&P 500

        Requirements:
        - Use only the provided input
        - Do not claim certainty
        - If evidence is weak or mixed, return neutral
        - Focus on macro, rates, inflation, earnings, labor, geopolitics, and risk sentiment
        - Treat sensational or low-information headlines as lower quality evidence
        - Return values that strictly fit the schema
        - Do not add any keys not defined by the schema
        - Assume the reader understands only the provided input was used for the analysis, don't need to explicitly state this in the output
        - Don't say "Using only these headlines" or similar in the output, just provide the analysis

        Input news JSON:
        {json.dumps(news_json, ensure_ascii=False)}
        """
    )

    html = render_market_report_html(analysis, title="Weekly Macro Market Brief")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    html_string_to_pdf(html, "report.pdf")

if __name__ == "__main__":
    main()
