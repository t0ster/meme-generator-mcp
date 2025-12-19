from typing import Literal

from pydantic import BaseModel


class TextPlaceholder(BaseModel):
    """Defines a text placeholder position and style on a meme template."""

    x: int
    y: int
    max_width: int
    align: Literal["left", "center", "right"] = "center"
    fill: str = "white"
    stroke_fill: str = "black"
    stroke_width: int = 2
    font_size: int = 40


class MemeConfig(BaseModel):
    template_file: str
    placeholders: dict[str, TextPlaceholder]
