import argparse
import copy
import threading
from pathlib import Path

import vigra  # somehow needed earlier to avoid import error later.
import dearpygui.dearpygui as dpg

from caactus.gui import descriptions, helpers
from caactus.gui.steps import STEPS, CaactusStep, run_step
from caactus.utils import get_config_step, load_config

STATE = {}

# ── Global parameter propagation map ────────────────────────────────────────
# Maps each global UI key to the (step_name, param_key) pairs it controls.
GLOBAL_PARAM_MAP = {
    "pixel_size":           [("CSV summary",              "pixel_size")],
    "variable_names":       [("Summary statistics",       "variable_names"),
                             ("PLN modelling",            "variable_names")],
    "class_order":          [("Summary statistics",       "class_order"),
                             ("PLN modelling",            "class_order")],
    "color_mapping":        [("Summary statistics",       "color_mapping")],
    "eucast_class_order":   [("EUCAST Summary statistics","class_order")],
    "eucast_color_mapping": [("EUCAST Summary statistics","color_mapping")],
    "conc_order":           [("EUCAST Summary statistics","conc_order")],
    "timepoint_order":      [("EUCAST Summary statistics","timepoint_order")],
}

# Params already covered by the global panel — hidden from per-step advanced sections.
GLOBAL_COVERED: frozenset = frozenset(
    target for targets in GLOBAL_PARAM_MAP.values() for target in targets
) | {
    # EUCAST variable_names is vestigial (the function ignores it)
    ("EUCAST Summary statistics", "variable_names"),
}

# Keys whose values are filesystem paths — get a Browse button.
PATH_KEYS = {"input_path", "output_path", "main_folder"}


# ── Directory-picker helper ──────────────────────────────────────────────────

def make_browse_callback(step_name: str, param_name: str, input_tag: str):
    """Return a button callback that opens a directory-picker dialog."""
    dialog_tag = f"__dir__{input_tag}"

    def _on_selected(_sender, app_data):
        path = app_data.get("file_path_name", "").rstrip("/\\")
        if not path:
            return
        if step_name in STATE and isinstance(STATE[step_name], dict):
            STATE[step_name][param_name] = path
        dpg.set_value(input_tag, path)
        if param_name == "main_folder":
            STATE["main_folder"] = path
            STATE["Global settings"]["main_folder"] = path
            STATE["full_config"]["main_folder"] = path

    def callback(sender, app_data):
        if dpg.does_item_exist(dialog_tag):
            dpg.show_item(dialog_tag)
        else:
            dpg.add_file_dialog(
                directory_selector=True,
                show=True,
                callback=_on_selected,
                cancel_callback=lambda s, a: None,
                tag=dialog_tag,
                width=700,
                height=400,
            )

    return callback


# ── State initialisation ─────────────────────────────────────────────────────

def init_state(config):
    STATE["full_config"] = copy.deepcopy(config)
    STATE["main_folder"] = config["main_folder"]
    STATE["Global settings"] = {"main_folder": STATE["main_folder"]}

    for step in STEPS:
        key = step.config_key
        if key is None:
            continue
        if step.stages:
            for stage in step.stages:
                STATE[f"{step.name}__{stage}"] = copy.deepcopy(
                    get_config_step(config, f"{key}.{stage}")
                )
            STATE[f"{step.name}__current_stage"] = step.stages[0]
            STATE[step.name] = STATE[f"{step.name}__{step.stages[0]}"]
        else:
            STATE[step.name] = get_config_step(config, key)

    # Extract initial values for the global settings panel from their source steps.
    ss = STATE.get("Summary statistics", {})
    eu = STATE.get("EUCAST Summary statistics", {})
    STATE["globals"] = {
        "pixel_size":           str(STATE.get("CSV summary", {}).get("pixel_size", "0.454")),
        "variable_names":       str(ss.get("variable_names", ["strain", "timepoint"])),
        "class_order":          str(ss.get("class_order", [])),
        "color_mapping":        str(ss.get("color_mapping", {})),
        "eucast_class_order":   str(eu.get("class_order", [])),
        "eucast_color_mapping": str(eu.get("color_mapping", {})),
        "conc_order":           str(eu.get("conc_order", [])),
        "timepoint_order":      str(eu.get("timepoint_order", [])),
    }


# ── Callbacks ────────────────────────────────────────────────────────────────

def on_global_change(global_key: str):
    """Return a callback that updates STATE['globals'] and propagates to steps."""
    targets = GLOBAL_PARAM_MAP.get(global_key, [])

    def callback(sender, app_data):
        STATE["globals"][global_key] = app_data
        for step_name, param in targets:
            if step_name in STATE:
                STATE[step_name][param] = app_data

    return callback


def on_main_folder_change(sender, app_data):
    STATE["main_folder"] = app_data
    STATE["Global settings"]["main_folder"] = app_data
    STATE["full_config"]["main_folder"] = app_data


def on_param_change(step_name: str, param_name: str):
    def callback(sender, app_data):
        STATE[step_name][param_name] = app_data
    return callback


def on_stage_selected(step: CaactusStep):
    def callback(sender, app_data):
        new_stage = app_data
        old_stage = STATE.get(f"{step.name}__current_stage", step.stages[0])

        # Persist current UI values into the old stage's cache.
        STATE[f"{step.name}__{old_stage}"] = copy.deepcopy(STATE[step.name])

        # Load the new stage's cached values.
        new_params = STATE[f"{step.name}__{new_stage}"]
        STATE[step.name] = new_params
        STATE[f"{step.name}__current_stage"] = new_stage

        # Sync advanced-path widgets.
        for k, v in new_params.items():
            tag = f"adv__{step.name}__{k}"
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, str(v) if not isinstance(v, (str, bool, int, float)) else v)

        # Refresh the help-popup description for the new stage.
        if isinstance(step.description, dict):
            desc_tag = f"__help_desc__{step.name}"
            if dpg.does_item_exist(desc_tag):
                descriptions.render_description(step.description[new_stage], tag=desc_tag)

    return callback


def create_run_callback(step: CaactusStep):
    def callback(sender, app_data, user_data):
        dpg.set_item_label(sender, "Running...")
        dpg.disable_item(sender)
        dpg.configure_item("log_widget", tracked=True)

        def worker():
            assert step.func is not None
            try:
                run_step(
                    step.func,
                    {"main_folder": STATE["main_folder"]} | STATE[step.name],
                )
            finally:
                dpg.enable_item(sender)
                dpg.set_item_label(sender, "Run")
                dpg.configure_item("log_widget", tracked=False)

        threading.Thread(target=worker, daemon=True).start()

    return callback


# ── Help popups ──────────────────────────────────────────────────────────────

def _build_help_window(step: CaactusStep):
    """Create a hidden modal help window for a step (called before main window)."""
    win_tag = f"__help_win__{step.name}"
    desc_tag = f"__help_desc__{step.name}"

    desc = step.description
    if isinstance(desc, dict):
        desc = desc[step.stages[0]] if step.stages else next(iter(desc.values()))

    with dpg.window(
        label=f"Help — {step.name}",
        modal=True,
        show=False,
        tag=win_tag,
        width=740,
        height=560,
    ):
        with dpg.child_window(height=-50, border=False):
            descriptions.render_description(desc, tag=desc_tag)
        dpg.add_separator()
        dpg.add_button(
            label="Close",
            width=-1,
            callback=lambda: dpg.hide_item(win_tag),
        )


def make_help_callback(step: CaactusStep):
    win_tag = f"__help_win__{step.name}"

    def callback(sender, app_data):
        # Refresh description for the currently selected stage.
        if isinstance(step.description, dict):
            stage = STATE.get(
                f"{step.name}__current_stage",
                step.stages[0] if step.stages else "",
            )
            desc_tag = f"__help_desc__{step.name}"
            if stage and dpg.does_item_exist(desc_tag):
                descriptions.render_description(step.description[stage], tag=desc_tag)
        dpg.show_item(win_tag)

    return callback


# ── Per-step advanced paths section ─────────────────────────────────────────

def _build_advanced_section(step: CaactusStep):
    """Collapsible section with overridable path/misc params for a step."""
    params = STATE.get(step.name, {})
    visible = {
        k: v for k, v in params.items()
        if (step.name, k) not in GLOBAL_COVERED
    }
    if not visible:
        return

    with dpg.collapsing_header(label="Advanced paths", default_open=False):
        for key, value in visible.items():
            label = key.replace("_", " ").title()
            tag = f"adv__{step.name}__{key}"
            display = str(value) if not isinstance(value, (str, bool, int, float)) else value

            if key in PATH_KEYS:
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        label=f"{label}##{tag}",
                        default_value=display,
                        tag=tag,
                        width=340,
                        callback=on_param_change(step.name, key),
                    )
                    dpg.add_button(
                        label=f"Browse##{tag}",
                        width=70,
                        callback=make_browse_callback(step.name, key, tag),
                    )
            else:
                dpg.add_input_text(
                    label=label,
                    default_value=display,
                    tag=tag,
                    callback=on_param_change(step.name, key),
                )


# ── Global settings panel ────────────────────────────────────────────────────

def _build_global_settings():
    dpg.add_text("Global Settings", color=[200, 200, 200])
    dpg.add_separator()

    # Main folder row
    mf_tag = "global__main_folder"
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            label="Main Folder##mf",
            default_value=STATE["main_folder"],
            tag=mf_tag,
            width=420,
            callback=on_main_folder_change,
        )
        dpg.add_button(
            label="Browse##mf",
            width=70,
            callback=make_browse_callback("Global settings", "main_folder", mf_tag),
        )

    dpg.add_spacer(height=4)

    # Pixel size + Variable names
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            label="Pixel Size (µm)##ps",
            default_value=STATE["globals"]["pixel_size"],
            tag="global__pixel_size",
            width=80,
            callback=on_global_change("pixel_size"),
        )
        dpg.add_spacer(width=12)
        dpg.add_input_text(
            label="Variable Names##vn",
            default_value=STATE["globals"]["variable_names"],
            tag="global__variable_names",
            width=250,
            callback=on_global_change("variable_names"),
        )

    # Class order + Color mapping
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            label="Class Order##co",
            default_value=STATE["globals"]["class_order"],
            tag="global__class_order",
            width=300,
            callback=on_global_change("class_order"),
        )
        dpg.add_spacer(width=12)
        dpg.add_input_text(
            label="Color Mapping##cm",
            default_value=STATE["globals"]["color_mapping"],
            tag="global__color_mapping",
            width=300,
            callback=on_global_change("color_mapping"),
        )

    dpg.add_spacer(height=4)

    # EUCAST settings (collapsed by default)
    with dpg.collapsing_header(label="EUCAST Settings", default_open=False):
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Class Order##eco",
                default_value=STATE["globals"]["eucast_class_order"],
                tag="global__eucast_class_order",
                width=280,
                callback=on_global_change("eucast_class_order"),
            )
            dpg.add_spacer(width=12)
            dpg.add_input_text(
                label="Color Mapping##ecm",
                default_value=STATE["globals"]["eucast_color_mapping"],
                tag="global__eucast_color_mapping",
                width=280,
                callback=on_global_change("eucast_color_mapping"),
            )
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Conc Order##cor",
                default_value=STATE["globals"]["conc_order"],
                tag="global__conc_order",
                width=280,
                callback=on_global_change("conc_order"),
            )
            dpg.add_spacer(width=12)
            dpg.add_input_text(
                label="Timepoint Order##to",
                default_value=STATE["globals"]["timepoint_order"],
                tag="global__timepoint_order",
                width=280,
                callback=on_global_change("timepoint_order"),
            )


# ── Workflow step rows ───────────────────────────────────────────────────────

def _build_step_row(step: CaactusStep, number: int):
    """One step row + its collapsible advanced-paths section."""
    with dpg.group(horizontal=True):
        dpg.add_text(f"{number}. {step.name}")

        if step.stages:
            dpg.add_combo(
                items=step.stages,
                default_value=step.stages[0],
                tag=f"stage__{step.name}",
                width=100,
                callback=on_stage_selected(step),
            )
        else:
            dpg.add_spacer(width=108)

        if step.func is not None:
            dpg.add_button(
                label="Run",
                tag=f"run_btn__{step.name}",
                width=80,
                callback=create_run_callback(step),
            )
        else:
            # Ilastik step — indicate manual action required, no Run button.
            dpg.add_button(label="Ilastik", width=80, enabled=False)

        dpg.add_button(
            label="? Help",
            width=70,
            callback=make_help_callback(step),
        )

    _build_advanced_section(step)
    dpg.add_spacer(height=2)


def _build_workflow():
    seen_groups: list[str] = []
    number = 1

    for step in STEPS:
        if not step.group:
            continue  # skip Introduction and any unlisted steps

        if step.group not in seen_groups:
            seen_groups.append(step.group)
            if len(seen_groups) > 1:
                dpg.add_spacer(height=6)
            dpg.add_text(step.group, color=[160, 200, 255])
            dpg.add_separator()

        _build_step_row(step, number)
        number += 1


# ── Main UI builder ──────────────────────────────────────────────────────────

def build_ui():
    # Build all help windows up front (hidden; shown on demand).
    for step in STEPS:
        if step.group and step.description:
            _build_help_window(step)

    with dpg.window(label="caactus", autosize=True, tag="main"):

        # ── Global settings (fixed-height top panel) ──
        with dpg.child_window(height=200, border=True):
            _build_global_settings()

        dpg.add_spacer(height=4)

        # ── Workflow list (scrollable) ──
        with dpg.child_window(height=-210, border=True):
            _build_workflow()

        dpg.add_spacer(height=4)

        # ── Log + logo (bottom) ──
        with dpg.group(horizontal=True):
            with dpg.child_window(height=200, width=-212):
                dpg.add_input_text(
                    tag="log_widget",
                    multiline=True,
                    height=-1,
                    width=-1,
                    readonly=True,
                    tracked=True,
                    track_offset=1,
                )
            logo = descriptions.load_texture_from_package("images/logo.png")
            dpg.add_image(logo, width=200, height=200, tag="logo")

    helpers.DPGLogger("log_widget")
    dpg.set_primary_window("main", True)


# ── Entry point ──────────────────────────────────────────────────────────────

def run_gui(config):
    dpg.create_context()
    helpers.load_font()
    helpers.set_theme()
    dpg.create_viewport(title="caactus", width=900, height=800)
    helpers.set_icons()
    init_state(config)
    build_ui()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=None, help="Path to config file")
    args = parser.parse_args()

    if args.config:
        config_path = Path(args.config)
    else:
        config_path = helpers.get_asset_path("default_config.toml")

    config = load_config(str(config_path))
    run_gui(config)


if __name__ == "__main__":
    main()
