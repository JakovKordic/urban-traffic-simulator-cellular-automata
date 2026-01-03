import random
import csv
from pathlib import Path

from ca import build_roads, seed_vehicles
from simulation import simulate
from utils.config_loader import load_config, load_scenarios, deep_update


def write_metrics_csv(path, metrics):
    """
    Snimi metrike u CSV.
    Stupci: t, vehicles, exits
    - vehicles: ima t=0..steps
    - exits: ima t=1..steps (za t=0 stavimo 0)
    """
    vehicles = metrics["vehicles_per_step"]
    exits = metrics["exits_per_step"]

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["t", "vehicles", "exits"])
        for t in range(len(vehicles)):
            ex = 0 if t == 0 else exits[t - 1]
            w.writerow([t, vehicles[t], ex])


def run_one(cfg, print_every=0):
    height = cfg["grid"]["height"]
    width = cfg["grid"]["width"]

    horizontal_rows = cfg["roads"]["horizontal_rows"]
    vertical_cols = cfg["roads"]["vertical_cols"]

    density = cfg["traffic"]["density"]
    steps = cfg["traffic"]["steps"]
    seed = cfg["traffic"]["seed"]

    reseed_cfg = cfg["traffic"].get("reseed", {})
    reseed_enabled = reseed_cfg.get("enabled", False)
    reseed_density = reseed_cfg.get("density", density)
    reseed_announce = reseed_cfg.get("announce", False)

    roads = build_roads(height, width, horizontal_rows, vertical_cols)

    rng0 = random.Random(seed)
    occ0 = seed_vehicles(roads, density=density, rng=rng0)

    occ_final, metrics = simulate(
        roads,
        occ0,
        steps=steps,
        seed=seed,
        print_every=print_every,
        reseed_on_empty=reseed_enabled,
        reseed_density=reseed_density,
        reseed_announce=reseed_announce,
    )
    return occ_final, metrics


def main():
    base_cfg = load_config("input/config.yaml")
    scenarios = load_scenarios("input/scenarios.yaml")

    print_every = base_cfg.get("render", {}).get("print_every", 1)

    if not scenarios:
        _, metrics = run_one(base_cfg, print_every=print_every)
        write_metrics_csv("output/base.csv", metrics)
        return

    for name, override in scenarios.items():
        cfg = deep_update(base_cfg, override)

        _, metrics = run_one(cfg, print_every=print_every)

        out_path = f"output/{name}.csv"
        write_metrics_csv(out_path, metrics)

        total_exits = sum(metrics["exits_per_step"])
        print(f"[{name}] završeno | ukupno izlazaka: {total_exits} | csv: {out_path}")


if __name__ == "__main__":
    main()
