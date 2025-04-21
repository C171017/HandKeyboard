### main.py
import cv2
import mediapipe as mp
import argparse
import time
from gestures import detect_pip, detect_tips, match_combo
from config import UNIVERSAL_THRESHOLD, DETERMINE_PERIOD_MS, GESTURE_KEY_MAP, SIDES
from pynput.keyboard import Controller

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=int, default=0,
                        help='0=built-in,1=external')
    args = parser.parse_args()

    keyboard = Controller()
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75
    )
    draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Per-hand state: flag, candidate tips, determine start time
    state = {
        side: {'active': False, 'cand': None, 'start': None}
        for side in SIDES
    }

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame.flags.writeable = False
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        frame.flags.writeable = True
        frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        now = time.time() * 1000
        # Current gestures per hand
        curr = {side: None for side in SIDES}

        if results.multi_hand_landmarks:
            for lm, hm in zip(results.multi_hand_landmarks,
                              results.multi_handedness):
                side = hm.classification[0].label.lower()
                # Group 1 immediate
                pip = detect_pip(lm.landmark)
                if pip:
                    curr[side] = f"{side}_g1_{pip}"
                else:
                    # Group 2 candidate
                    contacts = detect_tips(lm.landmark)
                    if len(contacts) >= 2:
                        combo = match_combo(contacts)
                        if combo:
                            # start determine period if not started
                            st = state[side]
                            if st['cand'] != combo:
                                st['cand'] = combo
                                st['start'] = now
                            # if elapsed, confirm
                            elif now - st['start'] >= DETERMINE_PERIOD_MS:
                                curr[side] = f"{side}_g2_{combo}"
                draw.draw_landmarks(frame, lm,
                                    mp.solutions.hands.HAND_CONNECTIONS)

        # Handle events and resetting
        for side in SIDES:
            s = state[side]
            if s['active']:
                # Wait until all joints are out of range to reset
                if detect_pip is None and len(detect_tips) == 0:
                    s.update(active=False, cand=None, start=None)
            else:
                g = curr[side]
                if g:
                    key = GESTURE_KEY_MAP.get(g)
                    if key:
                        keyboard.press(key)
                        keyboard.release(key)
                    s['active'] = True

        cv2.imshow('Hands', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()