import re
from dataclasses import dataclass
from typing import List, Literal

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image

from .helpers import get_asset_path, replace_single_newline

BlockType = Literal["paragraph", "image"]

@dataclass
class Block:
    type: BlockType
    content: str


IMG_PATTERN = re.compile(r"<([^<>]+)>")  # <filename.ext>


def parse_description(text: str) -> List[Block]:
    blocks: List[Block] = []
    pos = 0

    for match in IMG_PATTERN.finditer(text):
        start, end = match.span()

        # preceding paragraph
        if start > pos:
            paragraph = text[pos:start].strip()
            if paragraph:
                blocks.append(Block("paragraph", paragraph))

        # image
        blocks.append(Block("image", match.group(1).strip()))
        pos = end

    # trailing paragraph
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

def render_description(text: str):
    blocks = parse_description(text)

    for block in blocks:
        if block.type == "paragraph":
            dpg.add_text(replace_single_newline(block.content), wrap=0)

        elif block.type == "image":
            try:
                texture_tag = load_texture_from_package(block.content)
                dpg.add_image(texture_tag)
            except FileNotFoundError:
                dpg.add_text(f"[{block.content}]")
