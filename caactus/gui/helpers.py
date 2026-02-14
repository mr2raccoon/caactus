import sys
from importlib import resources

import dearpygui.dearpygui as dpg


def get_asset_path(path: str) -> str:
    """Return the absolute string path to an asset."""
    return str(resources.files("caactus").joinpath("gui/assets", path))

class DPGLogger:
    def __init__(self, tag):
        self.tag = tag
        self._log_buffer = ""

        self.stderr = sys.stderr
        self.stdout = sys.stdout
        sys.stdout = self
        sys.stderr = self

    def write(self, string):
        self.stdout.write(string)  # type: ignore
        current_text = dpg.get_value(self.tag)
        new_text = current_text + string
        dpg.set_value(self.tag, new_text)
        dpg.set_item_height(self.tag, int(dpg.get_text_size(new_text)[1] + 30))

    def flush(self):
        pass  # Required for file-like objects

    def close(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr


def load_font():
    font_path = get_asset_path("fonts/Inter-Regular.ttf")
    with dpg.font_registry():
        font = dpg.add_font(str(font_path), 20)

    dpg.bind_font(font)


def set_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 12, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)

    dpg.bind_theme(global_theme)


def set_icons(path: str = "logo.png"):
    icon_path = get_asset_path(path)
    dpg.set_viewport_small_icon(icon_path)
    dpg.set_viewport_large_icon(icon_path)


def make_button_themes():
    with dpg.theme(tag="enabled_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core
            )
    # - This theme should make the label text on the button red
    with dpg.theme(tag="disabled_theme"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(
                dpg.mvThemeCol_Text, (255, 0, 0), category=dpg.mvThemeCat_Core
            )
