from ca import DIRS

def print_state(roads, occ):
    """
    ASCII prikaz stanja.
    - '.' = nije cesta
    - '-' = horizontalna cesta (EW)
    - '|' = vertikalna cesta (NS)
    - '+' = raskrižje (NESW)
    - 'N','E','S','W' = vozilo (ako ih je više u istoj ćeliji, ispisuje '*')
    """
    h = len(roads)
    w = len(roads[0])

    for y in range(h):
        row_chars = []
        for x in range(w):
            allowed = roads[y][x]
            if allowed == "":
                row_chars.append(".")
                continue

            is_h = ("E" in allowed or "W" in allowed)
            is_v = ("N" in allowed or "S" in allowed)
            if is_h and is_v:
                base = "+"
            elif is_h:
                base = "-"
            else:
                base = "|"

            present_dirs = [d for d in DIRS if occ[d][y][x]]
            if len(present_dirs) == 0:
                row_chars.append(base)
            elif len(present_dirs) == 1:
                row_chars.append(present_dirs[0])
            else:
                row_chars.append("*")

        print("".join(row_chars))
