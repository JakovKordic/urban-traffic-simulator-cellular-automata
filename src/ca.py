import random

# Smjerovi kao znakovi radi
DIRS = ("N", "E", "S", "W")  # tuple jer je immutable
DXY = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}  # promjena (dy, dx)

PRIORITY = ("N", "E", "S", "W")  # pravilo prednosti autima

# Skretanja:
LEFT = {"N": "W", "W": "S", "S": "E", "E": "N"}
RIGHT = {"N": "E", "E": "S", "S": "W", "W": "N"}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def build_roads(height, width, horizontal_rows, vertical_cols):
    """
    Roads[y][x] je string dozvoljenih smjerova:
    "" (nije cesta), "EW", "NS", ili "EWNS" (raskrižje).
    """
    roads = []
    for _ in range(height):
        row = [""] * width
        roads.append(row)

    for y in horizontal_rows:
        if 0 <= y < height:
            for x in range(width):
                if "E" not in roads[y][x]:
                    roads[y][x] += "E"
                if "W" not in roads[y][x]:
                    roads[y][x] += "W"

    for x in vertical_cols:
        if 0 <= x < width:
            for y in range(height):
                if "N" not in roads[y][x]:
                    roads[y][x] += "N"
                if "S" not in roads[y][x]:
                    roads[y][x] += "S"

    return roads


def is_intersection(roads, y, x):
    """
    Ukoliko postoji "EWNS", funkcija to prepoznaje kao križanje i vraća True,
    u suprotnom vraća False.
    """
    return (
        roads[y][x].count("N")
        and roads[y][x].count("S")
        and roads[y][x].count("E")
        and roads[y][x].count("W")
    )


def empty_state(height, width):
    """
    Za svaki smjer kretanja (N, E, S, W) definira se zasebna 2D matrica
    dimenzija (height x width) koja označava prisutnost vozila (True / False).

    Razdvajanjem stanja po smjerovima omogućuje se modeliranje dvosmjernih
    i višetračnih cesta te se sprječavaju umjetne kolizije između vozila
    koja se nalaze na istoj koordinati, ali se kreću u različitim smjerovima.

    Potencijalni konflikti na raskrižjima ne rješavaju se u ovoj funkciji,
    već se obrađuju unutar funkcije za ažuriranje stanja (step).
    """
    occ = {}
    for d in DIRS:
        lane = []
        for _ in range(height):
            row = [False] * width
            lane.append(row)
        occ[d] = lane
    return occ


def seed_vehicles(roads, density, rng=None):
    """
    roads: 2D lista stringova, npr. "EW", "NS", "", "EWNS"
    density: broj između 0 i 1 (npr. 0.2 = 20% šanse)
    rng: generator slučajnih brojeva (opcionalno)

    Popunjava rječnik praznih matrica (generiran kroz empty_state funkciju) sa nasumično
    generiranim True vrijednostima koje predstavljaju vozila unutar
    nasumične matrice koja predstavlja inicijalni smjer kretanja.
    """
    if rng is None:
        rng = random.Random()

    h = len(roads)
    w = len(roads[0])
    occ = empty_state(h, w)

    for y in range(h):
        for x in range(w):
            allowed = roads[y][x]
            if allowed == "":
                continue
            for d in allowed:
                if rng.random() < density:
                    occ[d][y][x] = True
    return occ


def choose_turn(
    roads,
    y,
    x,
    incoming_dir,
    rng,
    p_straight=0.70,
    p_left=0.13,
    p_right=0.13,
    p_uturn=0.04,
):
    """
    Probabilistički odabire smjer na raskrižju:
    - ravno / lijevo / desno prema zadanim vjerojatnostima
    - U-turn ima nisku vjerojatnost (p_uturn)

    Ako preferirani smjer nije dopušten u toj ćeliji, pokušava s alternativama.
    """
    allowed = roads[y][x]

    straight = incoming_dir
    left = LEFT[incoming_dir]
    right = RIGHT[incoming_dir]
    uturn = OPPOSITE[incoming_dir]

    r = rng.random()
    if r < p_straight:
        first_choice = straight
    elif r < p_straight + p_left:
        first_choice = left
    elif r < p_straight + p_left + p_right:
        first_choice = right
    else:
        first_choice = uturn

    choices = [first_choice]
    for c in (straight, left, right, uturn):
        if c not in choices:
            choices.append(c)

    for c in choices:
        if c in allowed:
            return c

    return incoming_dir


def add_request(requests, key, item):
    """Dodaj item u requests[key]; ako key ne postoji, napravi praznu listu."""
    if key not in requests:
        requests[key] = []
    requests[key].append(item)


def step(roads, occ, rng=None):
    """
    Jedan CA korak (brzina 1) + skretanje na raskrižju.

    Promjena u odnosu na stariju verziju:
    - Izvan raskrižja konflikti se rješavaju PO TRAKAMA (out_dir),
      tj. ako dva vozila ulaze u istu ćeliju ali u različite smjerove/trake,
      oba se mogu upisati (dobiješ '*').
    - Ako više vozila želi u ISTU traku (isti out_dir) iste ćelije,
      pušta se jedno (winner), ostali ostaju.
    - Rub mape: vozilo koje bi izašlo iz mape nestaje (sink boundary).
    """
    if rng is None:
        rng = random.Random()

    h = len(roads)
    w = len(roads[0])
    next_occ = empty_state(h, w)

    # requests: ciljna ćelija -> lista kandidata (from_y, from_x, incoming_dir, out_dir)
    requests = {}
    exits = 0

    # 1) Generiranje zahtjeva
    for incoming_dir in DIRS:
        dy, dx = DXY[incoming_dir]
        for y in range(h):
            for x in range(w):
                if not occ[incoming_dir][y][x]:
                    continue

                ny, nx = y + dy, x + dx

                # izlazak iz mape -> vozilo nestaje
                if not (0 <= ny < h and 0 <= nx < w):
                    exits += 1
                    continue

                # ako ciljna ćelija ne podržava dolazni smjer -> ostani
                if incoming_dir not in roads[ny][nx]:
                    add_request(requests, (y, x), (y, x, incoming_dir, incoming_dir))
                    continue

                # odabir smjera nakon ulaska u raskrižje
                if is_intersection(roads, ny, nx):
                    out_dir = choose_turn(roads, ny, nx, incoming_dir, rng)
                else:
                    out_dir = incoming_dir

                # uspješan pokušaj ulaska u ciljnu ćeliju
                add_request(requests, (ny, nx), (y, x, incoming_dir, out_dir))

    # 2) Rješavanje zahtjeva i upis u next_occ
    for (ty, tx), candidates in requests.items():
        if len(candidates) == 1:
            fy, fx, incoming_dir, out_dir = candidates[0]
            next_occ[out_dir][ty][tx] = True
            continue

        if is_intersection(roads, ty, tx):
            # Na raskrižju puštaš samo jedno vozilo ukupno (po PRIORITY)
            winner = None
            for p in PRIORITY:
                for c in candidates:
                    if c[2] == p:  # incoming_dir
                        winner = c
                        break
                if winner is not None:
                    break

            if winner is None:
                winner = rng.choice(candidates)

            fy, fx, incoming_dir, out_dir = winner
            next_occ[out_dir][ty][tx] = True

            # ostali ostaju na mjestu u svojoj traci
            for fy2, fx2, incoming2, out2 in candidates:
                if (fy2, fx2, incoming2, out2) == winner:
                    continue
                next_occ[incoming2][fy2][fx2] = True

        else:
            # Nije raskrižje: rješavanje konflikta po traci (out_dir)
            by_lane = {}
            for c in candidates:
                lane = c[3]  # out_dir
                if lane not in by_lane:
                    by_lane[lane] = []
                by_lane[lane].append(c)

            # Za svaku traku u toj ćeliji odluči:
            for lane, lane_candidates in by_lane.items():
                if len(lane_candidates) == 1:
                    fy, fx, incoming_dir, out_dir = lane_candidates[0]
                    next_occ[out_dir][ty][tx] = True
                else:
                    # više vozila želi u ISTU traku iste ćelije -> pusti jedno
                    winner = rng.choice(lane_candidates)
                    fy, fx, incoming_dir, out_dir = winner
                    next_occ[out_dir][ty][tx] = True

                    # ostali ostaju na mjestu
                    for fy2, fx2, incoming2, out2 in lane_candidates:
                        if (fy2, fx2, incoming2, out2) == winner:
                            continue
                        next_occ[incoming2][fy2][fx2] = True

    return next_occ, exits