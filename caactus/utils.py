import tomli


def load_config(path="config.toml"):
    """Load a TOML configuration file."""
    with open(path, "rb") as f:
        return tomli.load(f)

def get_config_step(config: dict, key: str):
    data = config
    for section in key.split("."):
        data = data[section]
    return data
