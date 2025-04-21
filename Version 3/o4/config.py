### config.py
import string

# ----- Detection parameters -----
# Universal distance threshold for both Group 1 (pip) and Group 2 (tip combos)
UNIVERSAL_THRESHOLD = 0.08   # try 0.03–0.08
# Time to wait before confirming a tip combo (Group 2), in milliseconds
DETERMINE_PERIOD_MS = 100    # try 100–300

# ----- Joint definitions -----
# PIP joints for Group 1 detection: (index, name)
PIPS = [
    (6,  'index_pip'),
    (10, 'middle_pip'),
    (14, 'ring_pip'),
    (18, 'pinky_pip'),
]
# Tip joints for Group 2 detection: (index, finger_id)
# finger_id: 1=thumb,2=index,3=middle,4=ring,5=pinky
TIPS = [
    (8,  2),
    (12, 3),
    (16, 4),
    (20, 5),
]
# Valid Group 2 patterns: combinations that include thumb (1)
GROUP2_PATTERNS = [
    [1,2,3], [1,3,4], [1,4,5],
    [1,2,3,4], [1,3,4,5],
    [1,2,3,4,5],
]

# ----- Gesture / Key mapping -----
SIDES = ['left', 'right']
ALL_GESTURES = []
for side in SIDES:
    # Group 1 gestures
    for _, name in PIPS:
        ALL_GESTURES.append(f"{side}_g1_{name}")
    # Group 2 gestures
    for pattern in GROUP2_PATTERNS:
        ALL_GESTURES.append(f"{side}_g2_{''.join(map(str,pattern))}")

# Default mapping: a–z, then '1','2'
KEYS = list(string.ascii_lowercase) + ['1','2']
GESTURE_KEY_MAP = {g: KEYS[i] for i, g in enumerate(ALL_GESTURES)}