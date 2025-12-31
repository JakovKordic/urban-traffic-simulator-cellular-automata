import random

from ca import build_roads, seed_vehicles
from simulation import simulate
from utils.config_loader import load_config


def main():
    cfg = load_config("input/config.yaml")

    height = cfg["grid"]["height"]
    width = cfg["grid"]["width"]

    horizontal_rows = cfg["roads"]["horizontal_rows"]
    vertical_cols = cfg["roads"]["vertical_cols"]

    density = cfg["traffic"]["density"]
    steps = cfg["traffic"]["steps"]
    seed = cfg["traffic"]["seed"]

    roads = build_roads(height, width, horizontal_rows, vertical_cols)

    rng = random.Random(seed)
    occ0 = seed_vehicles(roads, density=density, rng=rng)

    simulate(roads, occ0, steps=steps, seed=seed, print_every=1)


if __name__ == "__main__":
    main()
