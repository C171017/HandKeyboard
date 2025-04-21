"""
Global, tweak‑at‑will parameters
All distances use MediaPipe’s **normalized 3‑D coordinates** (0…1).
"""

# ─── Landmark smoothing ─────────────────────────────────────────────
SMOOTHING_ALPHA: float = 0.7          # 0 = no smoothing, 1 = very smooth/slow

# ─── Group 1 (hysteresis & cooldown) ────────────────────────────────
THRESHOLD_G1_IN:  float = 0.03        # distance ≤ → gesture becomes active
THRESHOLD_G1_OUT: float = 0.06        # distance ≥ → gesture resets
COOLDOWN_G1:      float = 0.30        # s ‑ minimum gap between repeats

# ─── Group 2 (“combo” triggers) ─────────────────────────────────────
PRETRIGGER_DISTANCE: float = 0.01     # starts intent timer
THRESHOLD_GROUP2:   float = 0.01      # confirm radius after delay
DETERMINE_TIME:     float = 0.25      # s – wait before evaluating combo
COOLDOWN_G2:        float = 0.50      # s – gap between repeats