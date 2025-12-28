import random

# Smjerovi kao znakovi radi
DIRS = ("N", "E", "S", "W") # tuple jer je immutable
DXY = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)} # rječnik koji iz ključa smjera daje promjenu koordinata ovisno o smjeru kretnje

PRIORITY = ("N", "E", "S", "W") # tuple koji određuje pravilo prednosti autima

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
    
    # npr za height=4, width=4
    # [
    #  ["", "", "", ""],
    #  ["", "", "", ""],
    #  ["", "", "", ""],
    #  ["", "", "", ""]
    # ]
    
    for y in horizontal_rows:
        if 0 <= y < height:
            for x in range(width):
                if "E" not in roads[y][x]:
                    roads[y][x] += "E"
                if "W" not in roads[y][x]:
                    roads[y][x] += "W"
    # horizontal_rows - lista y koordinata kojima prolaze horizontalne ceste npr 1,3
    # [
    #  [""  , ""  , ""  , ""  ],
    #  ["EW", "EW", "EW", "EW"],
    #  [""  , ""  , ""  , ""  ],
    #  ["EW", "EW", "EW", "EW"]
    # ]
    
    for x in vertical_cols:
        if 0 <= x < width:
            for y in range(height):
                if "N" not in roads[y][x]:
                    roads[y][x] += "N"
                if "S" not in roads[y][x]:
                    roads[y][x] += "S"
    # vertical_cols - lista x koordinata kojima prolaze vertikalne ceste npr 1,3
    # [
    #  [""  , "NS"  , ""    , "NS"  ],
    #  ["EW", "EWNS", "EW  ", "EWNS"],
    #  [""  , "NS"  , ""    , "NS"  ],
    #  ["EW", "EWNS", "EW"  , "EWNS"]
    # ]
    return roads

def is_intersection(roads, y, x):
    """
    Ukoliko postoji "EWNS", funkcija to prepoznaje kao križanje i vraća True, u suprotnom vraća False
    """
    return roads[y][x].count("N") and roads[y][x].count("S") and roads[y][x].count("E") and roads[y][x].count("W")


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
        # za svaki smjer se kreira jedna 2d matrica koja po defaultu sadrži sve False, na početku nijedna ćelija nije occupied
        occ[d] = lane # sva četiri smjera se dodaju u rječnik occ

    return occ

def seed_vehicles(roads, density, rng=None):
    """
    roads: 2D lista stringova, npr. "EW", "NS", "", "EWNS"
    density: broj između 0 i 1 (npr. 0.2 = 20% šanse)
    rng: generator slučajnih brojeva (opcionalno)

    Popunjava rječnik praznih matrica (generiran kroz empty_state funkciju) sa nasumično
    generiranim True vrijednostima koje predstavljaju vozila unutar 
    nasumične matrice koja predstavlja inicijalni smjer kretanja
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
    roads, y, x, incoming_dir, rng,
    p_straight=0.70, p_left=0.13, p_right=0.13, p_uturn=0.04
):
    """
    Probabilistički odabire smjer na raskrižju:
    - ravno / lijevo / desno prema zadanim vjerojatnostima
    - U-turn ima nisku vjerojatnost (p_uturn)

    Ako preferirani smjer nije dopušten u toj ćeliji, pokušava s alternativama
    (prvo ostale opcije, a zadnje fallback).
    """
    allowed = roads[y][x]

    straight = incoming_dir
    left = LEFT[incoming_dir]
    right = RIGHT[incoming_dir]
    uturn = OPPOSITE[incoming_dir]

    # 1) Nasumično izaberi preferirani smjer
    r = rng.random()
    if r < p_straight:
        first_choice = straight
    elif r < p_straight + p_left:
        first_choice = left
    elif r < p_straight + p_left + p_right:
        first_choice = right
    else:
        first_choice = uturn

    # 2) Fallback redoslijed: prvo preferirani, zatim ostale opcije (da uvijek pronađe neki dopušten smjer ako postoji)
    choices = [first_choice]
    for c in (straight, left, right, uturn):
        if c not in choices:
            choices.append(c)

    # 3) Vrati prvu dopuštenu opciju
    for c in choices:
        if c in allowed:
            return c

    # 4) Sigurnosni fallback (ne bi se trebalo dogoditi)
    return incoming_dir


def step(roads, occ, rng=None):
    """
    Jedan CA korak (brzina 1) + skretanje na raskrižju.
    - Skuplja zahtjeve tko želi ući u koju ćeliju (requests)
    - Ako je target raskrižje, vozilo može promijeniti smjer (ravno/lijevo/desno)
    - Rješava konflikte: na raskrižju prolazi jedan po PRIORITY
    """
    if rng is None:
        rng = random.Random()

    h = len(roads)
    w = len(roads[0])
    next_occ = empty_state(h, w)

    # requests[(ty,tx)] = list of (from_y, from_x, incoming_dir, dir_after_move)
    requests = {} # rječnik koji vozilu pridružuje listu vrijednosti koje predstavljaju njegove trenutne 
    # koordinate, u kojem se smjeru kreće i smjer nakon prelaska u sljedeću stanicu

    # 1) generiraj zahtjeve
    for incoming_dir in DIRS:
        dy, dx = DXY[incoming_dir]
        for y in range(h):
            for x in range(w):
                if not occ[incoming_dir][y][x]:
                    continue

                # ako smjer nije dozvoljen u ovoj ćeliji -> ostani
                if incoming_dir not in roads[y][x]:
                    requests.setdefault((y, x), []).append((y, x, incoming_dir, incoming_dir))
                    continue

                ny, nx = y + dy, x + dx

                # rub mape: ostani
                if not (0 <= ny < h and 0 <= nx < w):
                    requests.setdefault((y, x), []).append((y, x, incoming_dir, incoming_dir))
                    continue

                # cilj mora podržavati dolazni smjer (da traka “nastavlja” u tu ćeliju)
                if incoming_dir not in roads[ny][nx]:
                    requests.setdefault((y, x), []).append((y, x, incoming_dir, incoming_dir))
                    continue

                # Ako ulaziš u raskrižje, odaberi novi smjer nakon ulaska
                if is_intersection(roads, ny, nx):
                    out_dir = choose_turn(roads, ny, nx, incoming_dir, rng)
                else:
                    out_dir = incoming_dir

                requests.setdefault((ny, nx), []).append((y, x, incoming_dir, out_dir))

    # 2) rješavanje zahtjeva i upis u next
    for (ty, tx), candidates in requests.items():
        if len(candidates) == 1:
            fy, fx, incoming_dir, out_dir = candidates[0]
            next_occ[out_dir][ty][tx] = True
            continue

        if is_intersection(roads, ty, tx):
            # pobjednik po PRIORITY se i dalje bira po incoming_dir (tko dolazi)
            winner = None
            for p in PRIORITY:
                for c in candidates:
                    if c[2] == p:  # c[2] je incoming_dir
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
            # nije raskrižje: konzervativno - nitko ne ulazi, svi ostaju
            for fy, fx, incoming_dir, out_dir in candidates:
                next_occ[incoming_dir][fy][fx] = True

    return next_occ

