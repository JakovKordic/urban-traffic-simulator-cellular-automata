from pathlib import Path
import yaml


def load_yaml(path):
    """Učita YAML i vrati dict."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"YAML datoteka ne postoji: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML mora biti dict na vrhu dokumenta: {path}")
    return data


def load_config(path="input/config.yaml"):
    """Učitava YAML konfiguraciju i vraća dict."""
    return load_yaml(path)


def load_scenarios(path="input/scenarios.yaml"):
    """
    Učitava scenarije.
    Očekuje format:
      naziv_scenarija:
        traffic: {density, steps, seed}
    """
    return load_yaml(path)


def deep_update(base, override):
    """
    Rekurzivno ažurira dict 'base' vrijednostima iz 'override'.
    - ako je vrijednost dict -> ide se dublje
    - inače se prepisuje
    Vraća NOVI dict (ne mijenja original).
    """
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_update(result[k], v)
        else:
            result[k] = v
    return result
