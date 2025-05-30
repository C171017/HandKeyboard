"""
Core gesture‑detection logic with:
 • Hysteresis for Group 1
 • Per‑gesture cooldowns for both groups
"""
from __future__ import annotations
import time
import math
from typing import Dict, List, Tuple

from pynput.keyboard import Controller, Key
import config
import mapping

keyboard = Controller()

# --------- helpers & constants ---------
_LANDMARK_PAIRS_G1 = [(4, 6), (4, 7), (4, 10), (4, 11),
                      (4, 14), (4, 15), (4, 18), (4, 19)]
_G2_TIPS          = [8, 12, 16, 20]


def _dist3(a, b) -> float:
    return math.sqrt(
        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2 +
        (a.z - b.z) ** 2
    )

def _get_reference_scale(lm: list) -> float:
    """Distance wrist (0) ↔ middle MCP (9), used to normalize z."""
    w, m = lm[0], lm[9]
    return math.sqrt(
        (w.x - m.x) ** 2 +
        (w.y - m.y) ** 2 +
        (w.z - m.z) ** 2
    )

def _norm_dist3(a, b, scale: float) -> float:
    """3D distance with z divided by the hand‐size scale."""
    dx = a.x - b.x
    dy = a.y - b.y
    dz = (a.z - b.z) / scale
    return math.sqrt(dx*dx + dy*dy + dz*dz)

class _HandState:
    """Per‑hand state store."""
    def __init__(self):
        # Hysteresis flags for Group 1
        self.g1_active: Dict[Tuple[int, int], bool] = {p: False for p in _LANDMARK_PAIRS_G1}
        # Cooldown tracking
        self.last_fire: Dict[str, float] = {}   # key → timestamp
        # Group 2 timer
        self.timer_start: float | None = None


class HandGestureDetector:
    def __init__(self):
        # "Left" and "Right" hand states
        self.state = {"Left": _HandState(), "Right": _HandState()}

    # ---------------------------------------------------------
    def _cooldown_ok(self,
                     s: _HandState,
                     key: str,
                     gap: float
                     ) -> bool:
        now = time.time()
        if now - s.last_fire.get(key, 0) >= gap:
            s.last_fire[key] = now
            return True
        return False

    # ---------------------------------------------------------
    def update(self, lm, hand_label: str) -> List[str]:
        out: List[str] = []
        s = self.state[hand_label]

        # compute per-frame hand-size scale
        scale = _get_reference_scale(lm)

        # --------- GROUP 1 (instant) ---------
        for pair in _LANDMARK_PAIRS_G1:
            dist = _norm_dist3(lm[pair[0]], lm[pair[1]], scale)
            active = s.g1_active[pair]

            if not active and dist <= config.THRESHOLD_G1_IN:
                key = mapping.GROUP1[hand_label].get(pair)
                if key and self._cooldown_ok(s, key, config.COOLDOWN_G1):
                    keyboard.press(key)
                    keyboard.release(key)
                    out.append(key)
                s.g1_active[pair] = True

            elif active and dist >= config.THRESHOLD_G1_OUT:
                s.g1_active[pair] = False

        # --------- GROUP 2 (combo) ---------
        thumb = lm[4]

        # Step 1 – intent detection
        if any(_norm_dist3(thumb, lm[t], scale) <= config.PRETRIGGER_DISTANCE for t in _G2_TIPS):
            if s.timer_start is None:
                s.timer_start = time.time()
        else:
            s.timer_start = None

        # Step 2 – timer matured → evaluate combo
        if s.timer_start and (time.time() - s.timer_start >= config.DETERMINE_TIME):
            combo = [4]
            for t in _G2_TIPS:
                if _norm_dist3(thumb, lm[t], scale) <= config.THRESHOLD_GROUP2:
                    combo.append(t)

            combo_t = tuple(sorted(combo))
            key = mapping.GROUP2[hand_label].get(combo_t)
            if key and self._cooldown_ok(s, key, config.COOLDOWN_G2):
                keyboard.press(key)
                keyboard.release(key)
                out.append(key)

            s.timer_start = None

        return out