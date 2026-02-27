import ast
import json
try:
    import tomllib as tomli  # Python 3.11+
except ModuleNotFoundError:
    import tomli  # Python 3.10

def load_config(path="config.toml"):
    """Load a TOML configuration file."""
    with open(path, "rb") as f:
        return tomli.load(f)

def get_config_step(config: dict, key: str):
    data = config
    for section in key.split("."):
        data = data[section]
    return data



def parse_if_needed(val):
    if not isinstance(val, str):
        return val

    s = val.strip()

    # 1 Try TOML (for inline tables / lists)
    try:
        return tomli.loads(f"val={s}")["val"]
    except tomli.TOMLDecodeError:
        pass

    # 2️Try JSON
    try:
        return json.loads(s)
    except Exception:
        pass

    # 3️Try Python literal (your GUI dict case)
    try:
        return ast.literal_eval(s)
    except Exception:
        pass

    # 4️⃣ Give up — return raw string
    return val