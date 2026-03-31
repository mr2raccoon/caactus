import re
from dataclasses import dataclass
from typing import List, Literal

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image

from .helpers import get_asset_path

BlockType = Literal["paragraph", "image"]

@dataclass
class Block:
    type: BlockType
    content: str


IMG_PATTERN = re.compile(r"<([^<>]+)>")  # <filename.ext>
_INLINE_RE  = re.compile(r"\*\*(.+?)\*\*|`(.+?)`")

# Colours used by the markdown renderer
_C_BOLD  = [255, 215, 90]
_C_CODE  = [100, 210, 180]
_C_H1    = [180, 220, 255]
_C_H2    = [160, 200, 240]
_C_H3    = [200, 200, 200]
_C_CAVE  = [255, 190, 60]
_C_NOTE  = [170, 210, 130]


def parse_description(text: str) -> List[Block]:
    blocks: List[Block] = []
    pos = 0

    for match in IMG_PATTERN.finditer(text):
        start, end = match.span()
        if start > pos:
            paragraph = text[pos:start].strip()
            if paragraph:
                blocks.append(Block("paragraph", paragraph))
        blocks.append(Block("image", match.group(1).strip()))
        pos = end

    if pos < len(text):
        paragraph = text[pos:].strip()
        if paragraph:
            blocks.append(Block("paragraph", paragraph))

    return blocks


def load_texture_from_package(filename: str) -> str:
    asset_path = get_asset_path(filename)
    with open(asset_path, "rb") as f:
        image = Image.open(f).convert("RGBA")
        data = np.array(image).astype(np.float32) / 255.0
        height, width, _ = data.shape

    texture_tag = f"tex::{filename}"
    if not dpg.does_item_exist(texture_tag):
        with dpg.texture_registry():
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=data.flatten().tolist(),
                tag=texture_tag,
            )

    return texture_tag


def _render_inline(text: str, parent: str, base_color: list | None = None):
    """Render one line of text, colouring **bold** and `code` spans."""
    segments: list[tuple[str, str]] = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            segments.append(("plain", text[pos:m.start()]))
        if m.group(1) is not None:
            segments.append(("bold", m.group(1)))
        else:
            segments.append(("code", m.group(2)))
        pos = m.end()
    if pos < len(text):
        segments.append(("plain", text[pos:]))

    if not segments:
        return

    has_inline = any(s[0] != "plain" for s in segments)

    if not has_inline:
        kw: dict = {"parent": parent, "wrap": 0}
        if base_color:
            kw["color"] = base_color
        dpg.add_text(text, **kw)
    else:
        with dpg.group(horizontal=True, parent=parent):
            for style, content in segments:
                if style == "bold":
                    dpg.add_text(content, color=_C_BOLD)
                elif style == "code":
                    dpg.add_text(content, color=_C_CODE)
                else:
                    if base_color:
                        dpg.add_text(content, color=base_color)
                    else:
                        dpg.add_text(content)


def _render_markdown_block(text: str, parent: str):
    """Render a paragraph with line-by-line markdown formatting."""
    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            dpg.add_spacer(height=3, parent=parent)
            continue

        # Headings
        if stripped.startswith("### "):
            dpg.add_text(stripped[4:], color=_C_H3, parent=parent, wrap=0)
        elif stripped.startswith("## "):
            dpg.add_text(stripped[3:], color=_C_H2, parent=parent, wrap=0)
            dpg.add_separator(parent=parent)
        elif stripped.startswith("# "):
            dpg.add_text(stripped[2:], color=_C_H1, parent=parent, wrap=0)
            dpg.add_separator(parent=parent)

        # CAVE / warning
        elif re.match(r"CAVE", stripped, re.IGNORECASE):
            _render_inline("⚠  " + stripped, parent=parent, base_color=_C_CAVE)

        # Note
        elif stripped.lower().startswith("note:"):
            _render_inline(stripped, parent=parent, base_color=_C_NOTE)

        # Bullet list
        elif stripped.startswith("- "):
            _render_inline("•  " + stripped[2:], parent=parent)

        # Numbered list (1. 2. etc.) — keep number, support inline formatting
        elif re.match(r"^\d+\.", stripped):
            _render_inline(stripped, parent=parent)

        # Plain text (may contain inline formatting)
        else:
            _render_inline(stripped, parent=parent)


def render_description(text: str, tag: str):
    blocks = parse_description(text)

    if dpg.get_alias_id(tag):
        dpg.delete_item(tag, children_only=True)
    else:
        dpg.add_group(tag=tag)

    for block in blocks:
        if block.type == "paragraph":
            _render_markdown_block(block.content, parent=tag)

        elif block.type == "image":
            try:
                texture_tag = load_texture_from_package(block.content)
                dpg.add_image(texture_tag, parent=tag)
            except FileNotFoundError:
                dpg.add_text(f"[{block.content}]", parent=tag)
