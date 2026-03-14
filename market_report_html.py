from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


DIRECTION_LABELS = {
    "up": "Bullish",
    "down": "Bearish",
    "neutral": "Neutral",
    "mixed": "Mixed",
}

CONFIDENCE_LABELS = {
    "low": "Low confidence",
    "medium": "Medium confidence",
    "high": "High confidence",
}


def _escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _normalize_direction(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"up", "down", "neutral", "mixed"} else "neutral"


def _normalize_confidence(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"low", "medium", "high"} else "medium"


def _direction_badge(direction: str) -> str:
    label = DIRECTION_LABELS.get(direction, "Neutral")
    return f'<span class="pill pill--direction pill--{_escape(direction)}">{_escape(label)}</span>'


def _confidence_badge(confidence: str) -> str:
    label = CONFIDENCE_LABELS.get(confidence, "Medium confidence")
    return f'<span class="pill pill--confidence pill--{_escape(confidence)}">{_escape(label)}</span>'


def _render_bias_card(title: str, bias: Mapping[str, Any]) -> str:
    direction = _normalize_direction(bias.get("direction"))
    confidence = _normalize_confidence(bias.get("confidence"))
    rationale = _escape(bias.get("rationale", "No rationale provided."))

    return f"""
        <article class="bias-card bias-card--{_escape(direction)}">
          <div class="bias-card__header">
            <h4>{_escape(title)}</h4>
            <div class="bias-card__meta">
              {_direction_badge(direction)}
              {_confidence_badge(confidence)}
            </div>
          </div>
          <p class="bias-card__body">{rationale}</p>
        </article>
    """


def _render_index_section(key: str, payload: Mapping[str, Any]) -> str:
    display_name = {
        "djia": "Dow Jones Industrial Average",
        "sp500": "S&P 500",
    }.get(key, key.replace("_", " ").upper())

    bias_1d = payload.get("bias_1d", {})
    bias_5d = payload.get("bias_5d", {})

    return f"""
      <section class="panel panel--index">
        <div class="panel__eyebrow">Index outlook</div>
        <h3 class="panel__title">{_escape(display_name)}</h3>
        <div class="bias-grid">
          {_render_bias_card("1 Day Bias", bias_1d)}
          {_render_bias_card("5 Day Bias", bias_5d)}
        </div>
      </section>
    """


def _render_list_panel(title: str, items: list[Any], panel_class: str = "") -> str:
    rendered_items = "".join(
        f'<li class="list-panel__item"><span>{_escape(item)}</span></li>'
        for item in items
    )
    return f"""
      <section class="panel list-panel {panel_class}">
        <h3 class="panel__title">{_escape(title)}</h3>
        <ul class="list-panel__list">
          {rendered_items}
        </ul>
      </section>
    """


def _render_summary_panel(title: str, text: str, tone_class: str = "") -> str:
    return f"""
      <section class="panel summary-panel {tone_class}">
        <h3 class="panel__title">{_escape(title)}</h3>
        <p class="summary-panel__text">{_escape(text)}</p>
      </section>
    """


def _render_sentiment(score: Any, final_summary: str) -> str:
    try:
        value = int(score)
    except (TypeError, ValueError):
        value = 0
    value = max(0, min(10, value))
    percent = value * 10

    if value <= 3:
        sentiment_label = "Cautious"
        sentiment_class = "sentiment--bearish"
    elif value <= 6:
        sentiment_label = "Balanced"
        sentiment_class = "sentiment--neutral"
    else:
        sentiment_label = "Constructive"
        sentiment_class = "sentiment--bullish"

    return f"""
      <section class="panel sentiment {sentiment_class}">
        <div class="sentiment__topline">Market sentiment</div>
        <div class="sentiment__row">
          <div class="sentiment__scoreblock">
            <div class="sentiment__score">{value}<span>/10</span></div>
            <div class="sentiment__label">{_escape(sentiment_label)}</div>
          </div>
          <div class="sentiment__meter-wrap">
            <div class="sentiment__meter">
              <div class="sentiment__meter-fill" style="width: {percent}%;"></div>
            </div>
            <p class="sentiment__summary">{_escape(final_summary)}</p>
          </div>
        </div>
      </section>
    """


def _render_report_date() -> str:
    formatted_date = datetime.now().strftime("%A, %B %d, %Y")
    return f"""
      <div class="hero__date-wrap">
        <div class="hero__date-label">Report Date</div>
        <div class="hero__date">{_escape(formatted_date)}</div>
      </div>
    """


def _build_html_document(data: Mapping[str, Any], title: str) -> str:
    djia = data.get("djia", {})
    sp500 = data.get("sp500", {})
    key_drivers = data.get("key_drivers", [])
    counterarguments = data.get("counterarguments", [])
    what_would_change_view = data.get("what_would_change_view", [])

    eli5 = data.get("eli5_summary", "")
    eli12 = data.get("eli12_summary", "")
    eli18 = data.get("eli18_summary", "")
    eli40 = data.get("eli40_summary", "")

    long_position_recommendation = data.get("long_position_recommendation", "")
    market_reentry_recommendation = data.get("market_reentry_recommendation", "")
    sentiment_score = data.get("sentiment_score", 0)
    final_vibe_summary = data.get("final_vibe_summary", "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(title)}</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --surface: rgba(255, 255, 255, 0.88);
      --surface-strong: rgba(255, 255, 255, 0.96);
      --text: #102033;
      --muted: #607089;
      --border: rgba(16, 32, 51, 0.10);
      --shadow: 0 18px 48px rgba(16, 32, 51, 0.10);
      --shadow-soft: 0 10px 24px rgba(16, 32, 51, 0.06);
      --radius-xl: 28px;
      --radius-lg: 22px;
      --radius-md: 16px;
      --bull: #117a57;
      --bull-soft: rgba(17, 122, 87, 0.10);
      --bear: #ad2338;
      --bear-soft: rgba(173, 35, 56, 0.10);
      --neutral: #7b61ff;
      --neutral-soft: rgba(123, 97, 255, 0.10);
      --amber: #b06a00;
      --amber-soft: rgba(176, 106, 0, 0.10);
      --line: rgba(16, 32, 51, 0.08);
      --page-width: 1240px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(123, 97, 255, 0.08), transparent 28%),
        radial-gradient(circle at top right, rgba(17, 122, 87, 0.07), transparent 24%),
        linear-gradient(180deg, #f8fafe 0%, #f3f6fb 100%);
      line-height: 1.6;
      letter-spacing: -0.01em;
    }}

    .page {{
      width: min(var(--page-width), calc(100% - 48px));
      margin: 40px auto 72px;
    }}

    .hero {{
      position: relative;
      overflow: hidden;
      padding: 52px 52px 40px;
      border: 1px solid var(--border);
      border-radius: 36px;
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.82)),
        linear-gradient(135deg, rgba(123, 97, 255, 0.08), rgba(17, 122, 87, 0.04));
      backdrop-filter: blur(18px);
      box-shadow: var(--shadow);
    }}

    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -80px -120px auto;
      width: 320px;
      height: 320px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(123, 97, 255, 0.12), transparent 70%);
      pointer-events: none;
    }}

    .hero__topbar {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }}

    .hero__eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      border: 1px solid rgba(16, 32, 51, 0.08);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.76);
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}

    .hero__eyebrow::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: linear-gradient(180deg, #7b61ff, #117a57);
    }}

    .hero__date-wrap {{
      padding: 10px 14px 11px;
      border: 1px solid rgba(16, 32, 51, 0.08);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.70);
      text-align: right;
      min-width: 220px;
    }}

    .hero__date-label {{
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      line-height: 1.2;
    }}

    .hero__date {{
      margin-top: 6px;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.25;
      color: var(--text);
    }}

    .hero__title {{
      margin: 18px 0 12px;
      max-width: 920px;
      font-size: clamp(34px, 4vw, 58px);
      line-height: 1.02;
      letter-spacing: -0.045em;
    }}

    .hero__subtitle {{
      max-width: 860px;
      margin: 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.8;
    }}

    .grid {{
      display: grid;
      gap: 24px;
      margin-top: 28px;
    }}

    .grid--2 {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .grid--3 {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}

    .panel {{
      padding: 30px;
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      background: var(--surface);
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-soft);
    }}

    .panel__eyebrow {{
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}

    .panel__title {{
      margin: 0 0 18px;
      font-size: 24px;
      line-height: 1.2;
      letter-spacing: -0.03em;
    }}

    .bias-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}

    .bias-card {{
      padding: 22px;
      border-radius: var(--radius-lg);
      border: 1px solid var(--line);
      background: var(--surface-strong);
    }}

    .bias-card--up {{
      background: linear-gradient(180deg, rgba(17, 122, 87, 0.08), rgba(255, 255, 255, 0.96));
    }}

    .bias-card--down {{
      background: linear-gradient(180deg, rgba(173, 35, 56, 0.08), rgba(255, 255, 255, 0.96));
    }}

    .bias-card--neutral,
    .bias-card--mixed {{
      background: linear-gradient(180deg, rgba(123, 97, 255, 0.08), rgba(255, 255, 255, 0.96));
    }}

    .bias-card__header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }}

    .bias-card__header h4 {{
      margin: 0;
      font-size: 18px;
      line-height: 1.25;
      letter-spacing: -0.02em;
    }}

    .bias-card__meta {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
    }}

    .bias-card__body {{
      margin: 0;
      color: #324256;
      font-size: 15px;
      line-height: 1.8;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      padding: 7px 11px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      border: 1px solid transparent;
      white-space: nowrap;
    }}

    .pill--up {{
      color: var(--bull);
      background: var(--bull-soft);
      border-color: rgba(17, 122, 87, 0.16);
    }}

    .pill--down {{
      color: var(--bear);
      background: var(--bear-soft);
      border-color: rgba(173, 35, 56, 0.16);
    }}

    .pill--neutral,
    .pill--mixed {{
      color: var(--neutral);
      background: var(--neutral-soft);
      border-color: rgba(123, 97, 255, 0.16);
    }}

    .pill--low {{
      color: var(--amber);
      background: var(--amber-soft);
      border-color: rgba(176, 106, 0, 0.16);
    }}

    .pill--medium {{
      color: #5c4a00;
      background: rgba(233, 199, 88, 0.18);
      border-color: rgba(176, 106, 0, 0.14);
    }}

    .pill--high {{
      color: var(--bull);
      background: var(--bull-soft);
      border-color: rgba(17, 122, 87, 0.16);
    }}

    .summary-panel__text {{
      margin: 0;
      color: #324256;
      font-size: 16px;
      line-height: 1.9;
    }}

    .list-panel__list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 14px;
    }}

    .list-panel__item {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }}

    .list-panel__item:first-child {{
      padding-top: 0;
      border-top: 0;
    }}

    .list-panel__item::before {{
      content: "";
      flex: 0 0 10px;
      width: 10px;
      height: 10px;
      margin-top: 9px;
      border-radius: 999px;
      background: linear-gradient(180deg, #7b61ff, #117a57);
      box-shadow: 0 0 0 5px rgba(123, 97, 255, 0.07);
    }}

    .list-panel__item span {{
      color: #324256;
      font-size: 15px;
      line-height: 1.8;
    }}

    .sentiment {{
      padding: 32px;
    }}

    .sentiment__topline {{
      margin-bottom: 18px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}

    .sentiment__row {{
      display: flex;
      align-items: center;
      gap: 28px;
    }}

    .sentiment__scoreblock {{
      min-width: 170px;
    }}

    .sentiment__score {{
      font-size: 52px;
      line-height: 1;
      letter-spacing: -0.05em;
      font-weight: 800;
    }}

    .sentiment__score span {{
      margin-left: 4px;
      font-size: 24px;
      color: var(--muted);
      font-weight: 700;
    }}

    .sentiment__label {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 15px;
      font-weight: 600;
    }}

    .sentiment__meter-wrap {{
      flex: 1;
    }}

    .sentiment__meter {{
      height: 14px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(16, 32, 51, 0.08);
      box-shadow: inset 0 1px 2px rgba(16, 32, 51, 0.05);
    }}

    .sentiment__meter-fill {{
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #ad2338 0%, #e5af37 55%, #117a57 100%);
    }}

    .sentiment__summary {{
      margin: 14px 0 0;
      color: #324256;
      font-size: 15px;
      line-height: 1.8;
    }}

    .recommendations {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
    }}

    .footer-note {{
      margin-top: 22px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}

    @media (max-width: 1080px) {{
      .grid--2,
      .grid--3,
      .recommendations,
      .bias-grid {{
        grid-template-columns: 1fr;
      }}

      .hero {{
        padding: 40px 28px 30px;
      }}

      .page {{
        width: min(var(--page-width), calc(100% - 28px));
        margin: 20px auto 48px;
      }}
    }}

    @media (max-width: 720px) {{
      .panel {{
        padding: 22px;
        border-radius: 22px;
      }}

      .hero__subtitle {{
        font-size: 16px;
      }}

      .hero__topbar {{
        flex-direction: column;
        align-items: stretch;
      }}

      .hero__date-wrap {{
        text-align: left;
        min-width: 0;
      }}

      .sentiment__row {{
        flex-direction: column;
        align-items: stretch;
      }}

      .bias-card__header {{
        flex-direction: column;
      }}

      .bias-card__meta {{
        justify-content: flex-start;
      }}
    }}

    @media print {{
      body {{
        background: #ffffff;
      }}

      .page {{
        width: 100%;
        margin: 0;
      }}

      .hero,
      .panel {{
        box-shadow: none;
        backdrop-filter: none;
        background: #ffffff;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="hero__topbar">
        <div class="hero__eyebrow">Market briefing</div>
        {_render_report_date()}
      </div>
      <h1 class="hero__title">{_escape(title)}</h1>
      <p class="hero__subtitle">{_escape(eli40 or final_vibe_summary or "Structured market view generated from the supplied JSON input.")}</p>
    </section>

    <div class="grid grid--2">
      {_render_index_section("djia", djia)}
      {_render_index_section("sp500", sp500)}
    </div>

    <div class="grid">
      {_render_sentiment(sentiment_score, final_vibe_summary)}
    </div>

    <div class="grid grid--2">
      {_render_summary_panel("Explain Like I'm 5", eli5)}
      {_render_summary_panel("Explain Like I'm 12", eli12)}
    </div>

    <div class="grid grid--2">
      {_render_summary_panel("Explain Like I'm 18", eli18)}
      {_render_summary_panel("Professional Summary", eli40)}
    </div>

    <div class="grid grid--3">
      {_render_list_panel("Key Drivers", key_drivers)}
      {_render_list_panel("Counterarguments", counterarguments)}
      {_render_list_panel("What Would Change the View", what_would_change_view)}
    </div>

    <div class="grid">
      <section class="panel">
        <h3 class="panel__title">Positioning and Reentry</h3>
        <div class="recommendations">
          <div>
            <div class="panel__eyebrow">Long position</div>
            <p class="summary-panel__text">{_escape(long_position_recommendation)}</p>
          </div>
          <div>
            <div class="panel__eyebrow">Reentry conditions</div>
            <p class="summary-panel__text">{_escape(market_reentry_recommendation)}</p>
          </div>
        </div>
      </section>
    </div>

    <p class="footer-note">Generated from structured JSON input.</p>
  </main>
</body>
</html>
"""


def _coerce_json_input(data: Any) -> Mapping[str, Any]:
    if isinstance(data, Mapping):
        return data
    if isinstance(data, str):
        return json.loads(data)
    raise TypeError("data must be a mapping or a JSON string")


def _read_json_file(path: str | Path) -> Mapping[str, Any]:
    with Path(path).expanduser().resolve().open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_text_file(path: str | Path, content: str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def _derive_title(data: Mapping[str, Any], title: str | None) -> str:
    if title and title.strip():
        return title.strip()
    vibe = str(data.get("final_vibe_summary", "")).strip()
    return "Market Outlook Report" if not vibe else "Market Outlook Report — Structured Brief"


"""
Render the supplied JSON object into a polished single-file HTML document.
"""
def render_market_report_html(data: Mapping[str, Any] | str, title: str | None = None) -> str:
    payload = _coerce_json_input(data)
    resolved_title = _derive_title(payload, title)
    return _build_html_document(payload, resolved_title)


"""
Read a JSON file, render it to HTML, and write the result to the output path.
"""
def json_file_to_html_file(
    input_json_path: str | Path,
    output_html_path: str | Path,
    title: str | None = None,
) -> Path:
    payload = _read_json_file(input_json_path)
    html_output = render_market_report_html(payload, title=title)
    return _write_text_file(output_html_path, html_output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a structured market JSON file into a polished HTML report."
    )
    parser.add_argument("input_json", help="Path to the input JSON file")
    parser.add_argument("output_html", help="Path to the output HTML file")
    parser.add_argument(
        "--title",
        default=None,
        help="Optional page title override",
    )

    args = parser.parse_args()
    output_path = json_file_to_html_file(
        input_json_path=args.input_json,
        output_html_path=args.output_html,
        title=args.title,
    )
    print(str(output_path))
