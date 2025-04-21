### gestures.py
import math
import config

def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def detect_pip(landmarks):
    """
    Check thumb-tip to each PIP joint.
    Return joint name if distance < threshold, else None.
    """
    for idx, name in config.PIPS:
        if _dist(landmarks[4], landmarks[idx]) < config.UNIVERSAL_THRESHOLD:
            return name
    return None


def detect_tips(landmarks):
    """
    Check thumb-tip to each fingertip.
    Return list of finger_ids whose tip is within threshold.
    """
    contacts = []
    for idx, fid in config.TIPS:
        if _dist(landmarks[4], landmarks[idx]) < config.UNIVERSAL_THRESHOLD:
            contacts.append(fid)
    return contacts


def match_combo(contacts):
    """
    Given list of finger_ids, prefix with 1 (thumb),
    return matching pattern or None.
    """
    pattern = [1] + sorted(contacts)
    for p in config.GROUP2_PATTERNS:
        if p == pattern:
            return ''.join(map(str, p))
    return None