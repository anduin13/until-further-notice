import sc_a, sc_b, sc_c, sc_d
def timeline():
    tl = []
    for m in (sc_a, sc_b, sc_c, sc_d):
        tl += m.timeline()
    return sorted(tl, key=lambda e: e[0])
