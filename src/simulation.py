import random
from ca import step
from scenes import print_state

def simulate(roads, occ, steps, seed=None, print_every=1):
    """
    Pokrene simulaciju 'steps' koraka.
    Uz proslijeđeni seed, dobije se reproducibilno skretanje i seeding.
    """
    rng = random.Random(seed)
    exits_per_step = []

    for t in range(steps + 1):
        if t % print_every == 0:
            print(f"\n--- t={t} ---")
            print_state(roads, occ)

        if t == steps:
            break

        occ, exits = step(roads, occ, rng=rng)
        exits_per_step.append(exits)
    return occ