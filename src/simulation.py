# src/simulation.py
import random

from ca import step
from scenes import print_state
from metrics import count_vehicles


def simulate(roads, occ, steps, seed=None, print_every=1):
    rng = random.Random(seed)

    exits_per_step = []
    vehicles_per_step = []

    # stanje u t=0
    vehicles_per_step.append(count_vehicles(occ))

    for t in range(steps):
        # prikaz (opcionalno)
        if print_every and (t % print_every == 0):
            print(f"\n--- t={t} ---")
            print_state(roads, occ)

        occ, exits = step(roads, occ, rng=rng)

        exits_per_step.append(exits)
        vehicles_per_step.append(count_vehicles(occ))

    return occ, {
        "exits_per_step": exits_per_step,
        "vehicles_per_step": vehicles_per_step,
    }
