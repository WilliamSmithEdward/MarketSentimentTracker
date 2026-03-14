from __future__ import annotations

from pathlib import Path
from typing import Union

from playwright.sync_api import sync_playwright


PathLike = Union[str, Path]


class HtmlToPdfError(RuntimeError):
    pass


def _resolve_path(path: PathLike) -> Path:
    return Path(path).expanduser().resolve()


def _build_file_url(path: Path) -> str:
    return path.resolve().as_uri()


"""
Convert an HTML file to PDF on Windows using Playwright Chromium.
This is the most reliable Python-first implementation on Windows because it avoids external CLI dependencies like wkhtmltopdf.
"""
def html_file_to_pdf(
    input_html_path: PathLike,
    output_pdf_path: PathLike,
    *,
    format: str = "A4",
    margin_top: str = "16mm",
    margin_right: str = "16mm",
    margin_bottom: str = "18mm",
    margin_left: str = "16mm",
    print_background: bool = True,
) -> Path:
    input_path = _resolve_path(input_html_path)
    output_path = _resolve_path(output_pdf_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input HTML file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(_build_file_url(input_path), wait_until="networkidle")
            page.pdf(
                path=str(output_path),
                format=format,
                print_background=print_background,
                margin={
                    "top": margin_top,
                    "right": margin_right,
                    "bottom": margin_bottom,
                    "left": margin_left,
                },
            )
            browser.close()
    except Exception as exc:
        raise HtmlToPdfError(str(exc)) from exc

    return output_path


"""
Convert an HTML string to PDF on Windows using Playwright Chromium.
This uses page.set_content for the most direct in-memory conversion path.
"""
def html_string_to_pdf(
    html: str,
    output_pdf_path: PathLike,
    *,
    format: str = "A4",
    margin_top: str = "16mm",
    margin_right: str = "16mm",
    margin_bottom: str = "18mm",
    margin_left: str = "16mm",
    print_background: bool = True,
) -> Path:
    output_path = _resolve_path(output_pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            page.pdf(
                path=str(output_path),
                format=format,
                print_background=print_background,
                margin={
                    "top": margin_top,
                    "right": margin_right,
                    "bottom": margin_bottom,
                    "left": margin_left,
                },
            )
            browser.close()
    except Exception as exc:
        raise HtmlToPdfError(str(exc)) from exc

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert HTML to PDF using Playwright on Windows.")
    parser.add_argument("input_html", help="Path to the input HTML file")
    parser.add_argument("output_pdf", help="Path to the output PDF file")
    parser.add_argument("--format", default="A4", help="PDF page format, e.g. A4 or Letter")
    args = parser.parse_args()

    result = html_file_to_pdf(
        input_html_path=args.input_html,
        output_pdf_path=args.output_pdf,
        format=args.format,
    )
    print(str(result))
