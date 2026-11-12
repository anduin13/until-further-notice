import importlib
MODS = ['v_a', 'v_b', 'v_c', 'v_d']
def timeline():
    tl = []
    for m in MODS:
        tl += importlib.import_module(m).timeline()
    return sorted(tl, key=lambda e: e[0])
