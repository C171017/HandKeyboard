"""
App entry.  Adds landmark smoothing before gesture detection.
"""
import cv2
import mediapipe as mp
import numpy as np

from gesture import HandGestureDetector
from smoothing import HandSmoother

def main():
    mp_hands = mp.solutions.hands.Hands(
        max_num_hands=2,
        model_complexity=1,          # ↑ quality  (2 = even better, slower)
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )
    detector  = HandGestureDetector()
    smoother  = HandSmoother()      # uses config.SMOOTHING_ALPHA

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # For tracking min/max z values
    min_z = float('inf')
    max_z = float('-inf')

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = mp_hands.process(frame_rgb)

            if res.multi_hand_landmarks and res.multi_handedness:
                for lm, handness in zip(res.multi_hand_landmarks,
                                        res.multi_handedness):
                    label = handness.classification[0].label  # "Left"/"Right"
                    smoothed_lm = smoother.smooth(label, lm.landmark)
                    detector.update(smoothed_lm, label)

                    # Get thumb tip and index tip coordinates
                    thumb_tip = smoothed_lm[4]  # thumb tip
                    index_tip = smoothed_lm[8]  # index tip
                    
                    # Update min/max z values
                    min_z = min(min_z, thumb_tip.z, index_tip.z)
                    max_z = max(max_z, thumb_tip.z, index_tip.z)

                    # Calculate 3D distance between thumb and index
                    dist_3d = np.sqrt(
                        (thumb_tip.x - index_tip.x) ** 2 +
                        (thumb_tip.y - index_tip.y) ** 2 +
                        (thumb_tip.z - index_tip.z) ** 2
                    )

                    # Calculate 2D distance (x,y only)
                    dist_2d = np.sqrt(
                        (thumb_tip.x - index_tip.x) ** 2 +
                        (thumb_tip.y - index_tip.y) ** 2
                    )

                    # Display coordinates and distances
                    info_text = [
                        f"Thumb Tip - x: {thumb_tip.x:.3f}, y: {thumb_tip.y:.3f}, z: {thumb_tip.z:.3f}",
                        f"Index Tip - x: {index_tip.x:.3f}, y: {index_tip.y:.3f}, z: {index_tip.z:.3f}",
                        f"3D Distance: {dist_3d:.3f}",
                        f"2D Distance: {dist_2d:.3f}",
                        f"Z Range - Min: {min_z:.3f}, Max: {max_z:.3f}"
                    ]

                    # Draw text on frame
                    for i, text in enumerate(info_text):
                        cv2.putText(frame, text, (10, 30 + i*30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Draw landmarks
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, lm, mp.solutions.hands.HAND_CONNECTIONS
                    )

            cv2.imshow("Hand Keyboard  –  ESC to quit", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()