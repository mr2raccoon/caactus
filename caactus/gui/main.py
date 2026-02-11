import argparse
import threading
from importlib import resources

import dearpygui.dearpygui as dpg

from caactus.gui import helpers
from caactus.gui.steps import STEPS, CaactusStep, run_step
from caactus.utils import get_config_step, load_config

STATE = {}


def init_state(config):
    STATE["main_folder"] = config["main_folder"]
    for step in STEPS:
        key = step.config_key
        if key is not None:
            STATE[step.name] = get_config_step(config, key)


def on_param_change(step_name: str, param_name: str):
    def callback(sender, app_data):
        STATE[step_name][param_name] = app_data

    return callback


def on_run_step(step: CaactusStep):
    def callback(sender, app_data, user_data):

        dpg.set_item_label(sender, "Running...")
        dpg.disable_item(sender)

        def worker():
            assert step.func is not None
            run_step(
                step.func,
                {"main_folder": STATE["main_folder"]} | STATE[step.name],
            )
            dpg.configure_item(sender, enabled=True)
            dpg.set_item_label(sender, "Run")

        threading.Thread(target=worker, daemon=True).start()

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


def build_step_tab(step: CaactusStep):
    step_name = step.name
    params = STATE.get(step_name, {})

    with dpg.tab(label=step_name):
        desc = step.description
        dpg.add_text(desc)
        dpg.add_separator()
        build_param_controls(step_name, params)
        dpg.add_separator()

        if step.func is not None:
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
    helpers.DPGLogger("log_widget")

    dpg.set_primary_window("main", True)


def run_gui(config):
    dpg.create_context()
    helpers.load_font()
    helpers.set_theme()
    dpg.create_viewport(
        title="caactus",
        width=800,
        height=600,
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
