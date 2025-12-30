import random
from ca import build_roads, seed_vehicles
from simulation import simulate

def main():
    height, width = 10, 20
    horizontal_rows = [2, 5, 8]
    vertical_cols = [4, 10, 16]

    roads = build_roads(height, width, horizontal_rows, vertical_cols)

    rng0 = random.Random(123)
    occ0 = seed_vehicles(roads, density=0.15, rng=rng0)

    simulate(roads, occ0, steps=20, seed=999, print_every=1)

if __name__ == "__main__":
    main()