import argparse
import threading

import dearpygui.dearpygui as dpg

from caactus.gui import helpers
from caactus.gui.steps import STEPS, CaactusStep, run_step
from caactus.utils import get_config_step, load_config

STATE = {}


def init_state(config):
    STATE["full_config"] = config
    STATE["main_folder"] = config["main_folder"]
    for step in STEPS:
        key = step.config_key
        if key is not None:
            STATE[step.name] = get_config_step(config, key)


def on_param_change(step_name: str, param_name: str):
    def callback(sender, app_data):
        STATE[step_name][param_name] = app_data

    return callback


def create_run_step_callback(step: CaactusStep):
    def callback(sender, app_data, user_data):

        dpg.set_item_label(sender, "Running...")
        dpg.disable_item(sender)

        def worker():
            assert step.func is not None
            try:
                run_step(
                    step.func,
                    {"main_folder": STATE["main_folder"]} | STATE[step.name],
                )
            finally:
                dpg.configure_item(sender, enabled=True)
                dpg.set_item_label(sender, "Run")

        threading.Thread(target=worker, daemon=True).start()

    return callback


def build_param_controls(step_name, params, tag_prefix=""):
    for key, value in params.items():
        label = key.replace("_", " ").title()

        ui_element = dpg.add_input_text
        if isinstance(value, bool):
            ui_element = dpg.add_checkbox
        elif isinstance(value, int):
            ui_element = dpg.add_input_int
        elif isinstance(value, float):
            ui_element = dpg.add_input_float
        elif isinstance(value, str):
            ui_element = dpg.add_input_text

        ui_element(
            label=label,
            default_value=value,  # type: ignore
            callback=on_param_change(step_name, key),
            tag=tag_prefix + key,
        )


def build_step_tab(step: CaactusStep):
    params = STATE.get(step.name, {})

    with dpg.tab(label=step.name):
        desc = step.description
        dpg.add_text(desc)
        dpg.add_separator()
        build_param_controls(step.name, params, tag_prefix=step.name)
        dpg.add_separator()

        if step.func is not None:
            dpg.add_button(
                label="Run",
                callback=create_run_step_callback(step),
                width=250,
                height=60,
            )


def build_ui():
    with dpg.window(label="caactus", autosize=True, tag="main"):
        with dpg.child_window(height=-210):
            build_param_controls(
                "Global settings", {"main_folder": STATE["main_folder"]}
            )
            dpg.add_separator()
            with dpg.tab_bar():
                for step in STEPS:
                    build_step_tab(step)

        with dpg.child_window(height=200):
            dpg.add_input_text(
                tag="log_widget",
                multiline=True,
                width=-1,
                height=-1,
                readonly=True,
                tracked=True,
                track_offset=1,
            )
    helpers.DPGLogger("log_widget")

    dpg.set_primary_window("main", True)


def run_gui(config):
    dpg.create_context()
    helpers.load_font()
    helpers.set_theme()
    dpg.create_viewport(
        title="caactus",
        width=800,
        height=760,
    )
    helpers.set_icons()
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
