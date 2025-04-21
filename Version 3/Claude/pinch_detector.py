# pinch_detector.py - Optimized pinch detection with progressive tracking

import numpy as np
import time
import cv2
import config
from pynput.keyboard import Controller

class PinchDetector:
    def __init__(self):
        """Initialize efficient pinch detector with progressive tracking"""
        self.keyboard = Controller()
        self.last_keystroke_time = 0
        self.history_length = config.APPROACH_HISTORY_LENGTH
        
        # Tracking dictionaries - use defaultdict pattern to simplify code
        self.distance_history = {}
        self.approaching = {}
        self.min_distances = {}
        self.pinch_triggered = {}
        
    def detect_pinches(self, hands_data, frame=None):
        """Detect pinches between thumb and finger segments with progressive tracking"""
        detected_keys = set()
        pinch_candidates = {}
        current_time = time.time()
        
        # Process both hands
        for hand_idx, hand_type in enumerate([("left_hand", 0), ("right_hand", 1)]):
            hand_name, hand_code = hand_type
            hand_landmarks = hands_data.get(hand_name)
            
            if hand_landmarks is None or len(hand_landmarks) <= config.THUMB_TIP:
                continue
                
            # Get thumb tip position
            thumb_tip = hand_landmarks[config.THUMB_TIP]
            
            # Iterate through all finger segments
            for finger_idx, finger_landmarks in enumerate(config.FINGER_LANDMARKS):
                for segment_idx, landmark_idx in enumerate(finger_landmarks):
                    if landmark_idx >= len(hand_landmarks):
                        continue
                    
                    # Calculate distance
                    finger_point = hand_landmarks[landmark_idx]
                    distance = np.linalg.norm(thumb_tip - finger_point)
                    
                    # Create unique pinch key
                    pinch_key = (hand_code, finger_idx, segment_idx)
                    
                    # Initialize tracking for new pinch points
                    if pinch_key not in self.distance_history:
                        self.distance_history[pinch_key] = [distance] * self.history_length
                        self.approaching[pinch_key] = False
                        self.min_distances[pinch_key] = float('inf')
                        self.pinch_triggered[pinch_key] = False
                    
                    # Update distance history
                    self.distance_history[pinch_key].pop(0)
                    self.distance_history[pinch_key].append(distance)
                    
                    # Check if consistently approaching
                    is_approaching = all(self.distance_history[pinch_key][i] > self.distance_history[pinch_key][i+1] 
                                       for i in range(self.history_length-1))
                    
                    # Detect pinch completion
                    if self.approaching[pinch_key] and not is_approaching:
                        if (self.min_distances[pinch_key] < config.PINCH_THRESHOLD and 
                            not self.pinch_triggered[pinch_key]):
                            # Add to candidate pinches
                            pinch_candidates[pinch_key] = self.min_distances[pinch_key]
                            self.pinch_triggered[pinch_key] = True
                        
                        # Reset minimum distance for next approach
                        self.min_distances[pinch_key] = float('inf')
                    
                    # Update approach status
                    self.approaching[pinch_key] = is_approaching
                    
                    # Update minimum distance if approaching
                    if is_approaching and distance < self.min_distances[pinch_key]:
                        self.min_distances[pinch_key] = distance
                    
                    # Reset trigger when fingers move apart
                    if distance > config.PINCH_THRESHOLD * 2:
                        self.pinch_triggered[pinch_key] = False
                    
                    # Visualize pinch point if frame is provided
                    if frame is not None and config.VISUALIZE_PINCHES:
                        self._visualize_pinch(frame, thumb_tip, finger_point, 
                                             pinch_key, distance, is_approaching)
        
        # Select and trigger the best pinch candidate
        if pinch_candidates and current_time - self.last_keystroke_time > config.KEYSTROKE_COOLDOWN:
            best_pinch = min(pinch_candidates.items(), key=lambda x: x[1])[0]
            
            if best_pinch in config.KEY_MAPPINGS:
                key = config.KEY_MAPPINGS[best_pinch]
                detected_keys.add(key)
                
                # Send keystroke
                self.keyboard.press(key)
                self.keyboard.release(key)
                self.last_keystroke_time = current_time
                
                # Visualize key press
                if frame is not None and config.SHOW_KEY_PRESSED:
                    self._show_key_pressed(frame, key)
        
        return detected_keys, frame
    
    def _visualize_pinch(self, frame, thumb_point, finger_point, pinch_key, distance, is_approaching):
        """Visualize the pinch with color-coded status"""
        h, w, _ = frame.shape
        
        # Convert normalized coordinates to pixels
        x1, y1 = int(thumb_point[0] * w), int(thumb_point[1] * h)
        x2, y2 = int(finger_point[0] * w), int(finger_point[1] * h)
        
        # Determine color based on status
        if is_approaching:
            color = (0, 255, 0) if distance < config.PINCH_THRESHOLD else (0, 255, 255)
        else:
            color = (255, 0, 0) if distance < config.PINCH_THRESHOLD else (128, 128, 128)
        
        # Thickness based on proximity
        thickness = max(1, min(3, int(5 * (1 - distance / 0.2))))
        
        # Draw visualization elements
        cv2.line(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.circle(frame, (x1, y1), config.PINCH_CIRCLE_RADIUS, color, -1)
        cv2.circle(frame, (x2, y2), config.PINCH_CIRCLE_RADIUS, color, -1)
        
        # Draw distance and key label if mapped
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.putText(frame, f"{distance:.2f}", (mid_x, mid_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        if pinch_key in config.KEY_MAPPINGS:
            key = config.KEY_MAPPINGS[pinch_key]
            cv2.putText(frame, key, (mid_x, mid_y + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def _show_key_pressed(self, frame, key):
        """Show key press notification in top-right corner"""
        h, w, _ = frame.shape
        
        # Create highlight box
        cv2.rectangle(frame, (w - 180, 10), (w - 10, 60), (0, 100, 0), -1)
        cv2.rectangle(frame, (w - 180, 10), (w - 10, 60), (0, 255, 0), 2)
        
        # Show key press
        cv2.putText(frame, "KEY:", (w - 170, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, key.upper(), (w - 110, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)