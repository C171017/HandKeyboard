"""
Static gesture‑to‑keystroke tables.
Edit freely – the detector imports this on every run.
Hand labels come straight from MediaPipe (“Left”, “Right”).
"""

# ---------- Group 1 : (4,X) 3‑D distance < THRESHOLD_GROUP1 ----------
GROUP1 = {
    "Left": {
        # (thumb tip, joint)  : key to press
        (4,  6): "q",
        (4,  7): "w",
        (4, 10): "e",
        (4, 11): "r",
        (4, 14): "t",
        (4, 15): "y",
        (4, 18): "u",
        (4, 19): "i",
    },
    "Right": {
        (4,  6): "o",
        (4,  7): "p",
        (4, 10): "a",
        (4, 11): "s",
        (4, 14): "d",
        (4, 15): "f",
        (4, 18): "g",
        (4, 19): "h",
    },
}

# ---------- Group 2 : thumb tip + finger‑TIP combos ----------
# Combos **must be tuples of landmark IDs, sorted ascending**.
GROUP2 = {
    "Left": {
        (4,  8)                 : "z",
        (4, 12)                 : "x",
        (4, 16)                 : "c",
        (4, 20)                 : "v",
        (4,  8, 12)             : "b",
        (4, 12, 16)             : "n",
        (4, 16, 20)             : "m",
        (4,  8, 12, 16)         : ",",
        (4, 12, 16, 20)         : ".",
        (4,  8, 12, 16, 20)     : "/",
    },
    "Right": {
        (4,  8)                 : "1",
        (4, 12)                 : "2",
        (4, 16)                 : "3",
        (4, 20)                 : "4",
        (4,  8, 12)             : "5",
        (4, 12, 16)             : "6",
        (4, 16, 20)             : "7",
        (4,  8, 12, 16)         : "8",
        (4, 12, 16, 20)         : "9",
        (4,  8, 12, 16, 20)     : "0",
    },
}