import tomli


def load_config(path="config.toml"):
    """Load a TOML configuration file."""
    with open(path, "rb") as f:
        return tomli.load(f)
