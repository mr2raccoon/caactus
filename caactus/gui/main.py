import argparse
import sys
from importlib import resources

import dearpygui.dearpygui as dpg

from caactus.gui.steps import STEPS, run_step
from caactus.utils import get_config_step, load_config

STATE = {}


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
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)

    dpg.bind_theme(global_theme)


def init_state(config):
    STATE["main_folder"] = config["main_folder"]
    for step in STEPS:
        key = step["config_key"]
        if key is not None:
            STATE[step["name"]] = get_config_step(config, step["config_key"])


def on_param_change(step_name, param_name):
    def callback(sender, app_data):
        STATE[step_name][param_name] = app_data

    return callback


def on_run_step(step):
    def callback():
        run_step(
            step["func"],
            {"main_folder": STATE["main_folder"]} | STATE[step["name"]],
        )

    return callback


def build_param_controls(step_name, params):
    for key, value in params.items():
        if isinstance(value, bool):
            dpg.add_checkbox(
                label=key,
                default_value=value,
                callback=on_param_change(step_name, key),
            )
        elif isinstance(value, int):
            dpg.add_input_int(
                label=key,
                default_value=value,
                callback=on_param_change(step_name, key),
            )
        elif isinstance(value, float):
            dpg.add_input_float(
                label=key,
                default_value=value,
                callback=on_param_change(step_name, key),
            )
        else:
            dpg.add_input_text(
                label=key,
                default_value=str(value),
                callback=on_param_change(step_name, key),
            )


def build_step_tab(step):
    step_name = step["name"]
    params = STATE.get(step_name, {})

    with dpg.tab(label=step_name):
        desc = step.get("description", "")
        dpg.add_text(desc)
        dpg.add_separator()
        build_param_controls(step_name, params)
        dpg.add_separator()

        if step.get("func", None) is not None:
            dpg.add_button(
                label="Run", callback=on_run_step(step), width=250, height=60
            )


def build_ui():
    with dpg.window(label="caactus", autosize=True, tag="main"):
        build_param_controls("Global settings", {"main_folder": STATE["main_folder"]})
        dpg.add_separator()
        with dpg.tab_bar():
            for step in STEPS:
                build_step_tab(step)
        with dpg.child_window():
            dpg.add_input_text(
                tag="log_widget",
                multiline=True,
                width=-1,
                height=-1,
                readonly=True,
                tracked=True,
                track_offset=1,
            )
    DPGLogger("log_widget")

    dpg.set_primary_window("main", True)


def run_gui(config):
    dpg.create_context()
    load_font()
    set_theme()
    icon_path = get_asset_path("favicon.ico")
    dpg.create_viewport(
        title="caactus",
        width=800,
        height=600,
    )
    dpg.set_viewport_small_icon(icon_path)
    dpg.set_viewport_large_icon(icon_path)
    init_state(config)
    build_ui()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="config.toml", help="Path to config file"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    run_gui(config)


if __name__ == "__main__":
    main()
