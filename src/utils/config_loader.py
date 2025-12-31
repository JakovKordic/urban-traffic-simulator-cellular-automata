from pathlib import Path
import yaml

def load_config(path="input/config.yaml"):
    """
    Učitava YAML konfiguraciju i vraća dict.
    Pretpostavlja ispravnu strukturu config datoteke.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config