"""
Exponential moving‑average smoother for MediaPipe landmarks
"""
from __future__ import annotations
from typing import Dict, List
from mediapipe.framework.formats import landmark_pb2
import config


class HandSmoother:
    def __init__(self, alpha: float = config.SMOOTHING_ALPHA):
        self.alpha = alpha
        self.prev: Dict[str, List[landmark_pb2.NormalizedLandmark]] = {}

    # ---------------------------------------------------------
    def smooth(self,
               hand_label: str,
               cur: List[landmark_pb2.NormalizedLandmark]
               ) -> List[landmark_pb2.NormalizedLandmark]:
        """
        Returns a **new list** of smoothed landmarks.
        """
        if hand_label not in self.prev:
            # first frame → no smoothing yet
            self.prev[hand_label] = cur
            return cur

        out: List[landmark_pb2.NormalizedLandmark] = []
        for a, b in zip(cur, self.prev[hand_label]):
            lm = landmark_pb2.NormalizedLandmark()
            lm.x = self.alpha * a.x + (1 - self.alpha) * b.x
            lm.y = self.alpha * a.y + (1 - self.alpha) * b.y
            lm.z = self.alpha * a.z + (1 - self.alpha) * b.z
            out.append(lm)

        # update state & return
        self.prev[hand_label] = out
        return out