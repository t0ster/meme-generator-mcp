"""MCP server for generating memes with text overlays."""

import argparse
import time
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field
from PIL import Image, ImageDraw, ImageFont

from app.utils import get_fallback_font_path, get_meme_configs, get_output_dir, get_templates_dir, init, set_dev_mode


mcp = FastMCP("meme-generator")


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    lines: list[str] = []
    current_line: list[str] = []

    for word in text.upper().split():
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def generate_meme_image(
    meme_type: str, texts: dict[str, str], output_dir: Path
) -> Path:
    """Generate a meme image with the given texts."""
    config = get_meme_configs()[meme_type]
    template_path = get_templates_dir() / config.template_file

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {config.template_file}")

    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    for name, text in texts.items():
        placeholder = config.placeholders[name]
        try:
            font = ImageFont.truetype("Impact", placeholder.font_size)
        except OSError:
            try:
                font = ImageFont.truetype(str(get_fallback_font_path()), placeholder.font_size)
            except OSError:
                font = ImageFont.load_default(placeholder.font_size)

        lines = wrap_text(draw, text, font, placeholder.max_width)

        anchor_map = {"left": "la", "center": "ma", "right": "ra"}
        anchor = anchor_map[placeholder.align]

        y_offset = placeholder.y
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]

            draw.text(
                (placeholder.x, y_offset),
                line,
                font=font,
                fill=placeholder.fill,
                stroke_width=placeholder.stroke_width,
                stroke_fill=placeholder.stroke_fill,
                anchor=anchor,
            )
            y_offset += line_height + int(placeholder.font_size * 0.2)

    output_path = output_dir / f"{int(time.time())}_{meme_type}.jpg"
    img.save(output_path, "JPEG")
    return output_path


@mcp.tool()
async def generate_meme(
    meme_name: Annotated[str, Field(description="The type of meme to generate")],
    texts: Annotated[
        dict[str, str],
        Field(
            description=(
                'Dictionary like {"placeholder_name": "Your text here"}. '
                "To skip a placeholder, use an empty string explicitly."
            )
        ),
    ],
) -> dict:
    """
    Generate a meme with custom text overlays.

    Each meme type has specific named text placeholders that must be filled.
    Use the 'get_meme_info' tool to see available memes and their placeholder requirements.
    """
    try:
        meme_configs = get_meme_configs()
        if meme_name not in meme_configs:
            return {
                "status": "error",
                "message": f"Unknown meme type: {meme_name}",
                "available_memes": list(meme_configs.keys()),
            }

        config = meme_configs[meme_name]
        expected_keys = set(config.placeholders.keys())
        provided_keys = set(texts.keys())

        if provided_keys != expected_keys:
            missing = expected_keys - provided_keys
            extra = provided_keys - expected_keys
            error_parts = []
            if missing:
                error_parts.append(f"missing: {', '.join(missing)}")
            if extra:
                error_parts.append(f"unexpected: {', '.join(extra)}")
            msg = f"Meme '{meme_name}' placeholder mismatch. {'; '.join(error_parts)}."
            if missing:
                msg += " To skip a placeholder, use an empty string explicitly."
            raise ValueError(msg)

        saved_path = generate_meme_image(meme_name, texts, get_output_dir())

        return {
            "status": "success",
            "message": "Meme generated successfully",
            "output_path": str(saved_path.resolve()),
            "meme_type": meme_name,
            "texts_used": texts,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating meme: {str(e)}",
            "meme_type": meme_name,
        }


@mcp.tool()
async def get_meme_info(
    meme_name: Annotated[
        str | None, Field(description="Optional: Get info for a specific meme")
    ] = None,
) -> dict:
    """Get information about available memes and their text placeholder requirements."""
    meme_configs = get_meme_configs()
    if meme_name:
        if meme_name not in meme_configs:
            return {"status": "error", "message": f"Unknown meme type: {meme_name}"}

        config = meme_configs[meme_name]
        placeholder_names = list(config.placeholders.keys())
        return {
            "status": "success",
            "meme_name": meme_name,
            "template_file": config.template_file,
            "placeholder_names": placeholder_names,
            "example_usage": {
                "meme_name": meme_name,
                "texts": {name: f"Example {name}" for name in placeholder_names},
            },
        }
    else:
        all_memes = {}
        for meme_type, config in meme_configs.items():
            all_memes[meme_type] = {
                "placeholder_names": list(config.placeholders.keys()),
                "template_file": config.template_file,
            }

        return {
            "status": "success",
            "available_memes": all_memes,
            "total_memes": len(all_memes),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Use local app/ templates and configs")
    args = parser.parse_args()

    if args.dev:
        set_dev_mode(True)

    init()
    mcp.run()
