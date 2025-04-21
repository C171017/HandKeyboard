# config.py - Streamlined configuration settings for hand keyboard

# Pinch detection settings
PINCH_THRESHOLD = 0.05  # Distance threshold for pinch detection
KEYSTROKE_COOLDOWN = 0.5  # Seconds between keystrokes
APPROACH_HISTORY_LENGTH = 5  # Frames to check for consistent approach

# Finger landmark indices
THUMB_TIP = 4
FINGER_LANDMARKS = [
    [8, 7, 6],    # Index finger: tip, middle, base
    [12, 11, 10], # Middle finger: tip, middle, base
    [16, 15, 14], # Ring finger: tip, middle, base
    [20, 19, 18]  # Pinky finger: tip, middle, base
]

# Key mappings: (hand, finger, segment) -> key
# hand: 0=left, 1=right; finger: 0=index → 3=pinky; segment: 0=tip → 2=base
KEY_MAPPINGS = {
    # Left hand (a-l)
    (0, 0, 0): 'a', (0, 0, 1): 'b', (0, 0, 2): 'c',
    (0, 1, 0): 'd', (0, 1, 1): 'e', (0, 1, 2): 'f',
    (0, 2, 0): 'g', (0, 2, 1): 'h', (0, 2, 2): 'i',
    (0, 3, 0): 'j', (0, 3, 1): 'k', (0, 3, 2): 'l',
    
    # Right hand (m-x)
    (1, 0, 0): 'm', (1, 0, 1): 'n', (1, 0, 2): 'o',
    (1, 1, 0): 'p', (1, 1, 1): 'q', (1, 1, 2): 'r',
    (1, 2, 0): 's', (1, 2, 1): 't', (1, 2, 2): 'u',
    (1, 3, 0): 'v', (1, 3, 1): 'w', (1, 3, 2): 'x'
}

# Visualization settings
VISUALIZE_PINCHES = True
SHOW_KEY_PRESSED = True
TEXT_COLOR = (0, 255, 0)  # Green
PINCH_LINE_COLOR = (0, 255, 255)  # Yellow
PINCH_CIRCLE_RADIUS = 5

# Camera settings
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_FPS = 30