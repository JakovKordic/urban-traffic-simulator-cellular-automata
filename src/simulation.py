import random

from ca import step, seed_vehicles
from scenes import print_state
from metrics import count_vehicles


def simulate(
    roads,
    occ,
    steps,
    seed=None,
    print_every=1,
    reseed_on_empty=False,
    reseed_density=None,
    reseed_announce=False,
):
    """
    Pokreće simulaciju 'steps' koraka.

    - seed: reproducibilnost (skretanja, konflikti)
    - print_every: ASCII ispis svakih N koraka (0/None = bez ispisa)
    - reseed_on_empty: ako je True i broj vozila padne na 0 -> ponovno generira vozila
    - reseed_density: gustoća za ponovno generiranje (ako je None i reseed_on_empty=True -> greška)
    - reseed_announce: ako je True, ispiše poruku kad se dogodi reseed

    Vraća:
    (final_occ, metrics_dict)
    """
    rng = random.Random(seed)

    exits_per_step = []
    vehicles_per_step = []

    vehicles_per_step.append(count_vehicles(occ))

    for t in range(steps):
        if print_every and (t % print_every == 0):
            print(f"\n--- t={t} ---")
            print_state(roads, occ)

        occ, exits = step(roads, occ, rng=rng)

        if reseed_on_empty and count_vehicles(occ) == 0:
            if reseed_density is None:
                raise ValueError("reseed_density mora biti zadan ako reseed_on_empty=True")

            if reseed_announce:
                print(f"*** RESEED u t={t} ***")

            occ = seed_vehicles(roads, density=reseed_density, rng=rng)

        exits_per_step.append(exits)
        vehicles_per_step.append(count_vehicles(occ))

    return occ, {
        "exits_per_step": exits_per_step,
        "vehicles_per_step": vehicles_per_step,
    }
