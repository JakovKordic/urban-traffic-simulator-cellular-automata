from ca import DIRS

def count_vehicles(occ):
    """Ukupan broj vozila na mapi."""
    total = 0
    for d in DIRS:
        for row in occ[d]:
            for cell in row:
                if cell:
                    total += 1
    return total

def vehicles_per_direction(occ, d):
    """Broj vozila u jednom smjeru (d je 'N', 'E', 'S' ili 'W')."""
    total = 0
    for row in occ[d]:
        for cell in row:
            if cell:
                total += 1
    return total

def total_exits(exits_per_step):
    """
    Aproksimacija izlazaka (točno samo ako NEMA ulaza i nema drugih načina nestanka).
    """
    return sum(exits_per_step)
