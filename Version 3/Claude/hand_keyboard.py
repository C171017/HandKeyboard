# hand_keyboard.py - Streamlined hand gesture keyboard

import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import queue
import config
from pinch_detector import PinchDetector

# MediaPipe solutions
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class HandKeyboard:
    def __init__(self, 
                 static_image_mode=False,
                 max_num_hands=2,
                 model_complexity=1,
                 min_detection_confidence=0.7,
                 min_tracking_confidence=0.7,
                 camera_index=0):
        """Initialize optimized hand keyboard system"""
        # Hand tracking parameters
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.camera_index = camera_index
        
        # Initialize the pinch detector
        self.pinch_detector = PinchDetector()
        
        # Threading components
        self.input_queue = queue.Queue(maxsize=2)
        self.output_queue = queue.Queue(maxsize=2)
        self.running = False
        self.processing_thread = None
        
        # Position filtering for stability
        self.position_history = {
            "left_hand": [None] * 3,  # Reduced history length for efficiency
            "right_hand": [None] * 3
        }
        
        # Performance tracking
        self.fps_tracker = FPSTracker(30)  # Track past 30 frames
        
        # Initialize MediaPipe and camera later in start()
        self.hands = None
        self.cap = None
    
    def start(self):
        """Start the hand keyboard system"""
        # Initialize the webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Configure camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.DEFAULT_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.DEFAULT_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.DEFAULT_FPS)
        
        # Try hardware acceleration for Apple Silicon
        try:
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, 1)
        except:
            pass
        
        # Initialize MediaPipe hands
        self.hands = mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_num_hands,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence)
        
        # Start processing thread
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_frames)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Run main capture loop
        self._capture_frames()
    
    def stop(self):
        """Stop the hand keyboard system"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def _capture_frames(self):
        """Capture frames from webcam and manage processing flow"""
        try:
            while self.running and self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read from camera")
                    break
                
                # Add to input queue if not full
                if not self.input_queue.full():
                    self.input_queue.put((frame, time.time()), block=False)
                
                # Process results from output queue
                if not self.output_queue.empty():
                    processed_data = self.output_queue.get(block=False)
                    self._display_frame(processed_data)
                
                # Exit on 'q' key press
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
                
        except Exception as e:
            print(f"Error in capture frames: {e}")
        finally:
            self.stop()
    
    def _process_frames(self):
        """Process frames to detect hands and pinches in separate thread"""
        try:
            while self.running:
                if not self.input_queue.empty():
                    frame, timestamp = self.input_queue.get(block=False)
                    
                    # Time the processing
                    start_time = time.time()
                    
                    # Process frame for hand detection
                    processed_frame, hands_data = self._detect_hands(frame)
                    
                    # Filter positions for stability
                    filtered_hands_data = self._filter_hand_positions(hands_data)
                    
                    # Detect pinches and trigger keystrokes
                    detected_keys, processed_frame = self.pinch_detector.detect_pinches(
                        filtered_hands_data, processed_frame)
                    
                    # Track FPS
                    elapsed = time.time() - timestamp
                    fps = 1 / elapsed if elapsed > 0 else 0
                    self.fps_tracker.update(fps)
                    
                    # Add results to output queue if not full
                    if not self.output_queue.full():
                        self.output_queue.put((
                            processed_frame, 
                            filtered_hands_data, 
                            detected_keys, 
                            self.fps_tracker.get_avg_fps(),
                            time.time() - start_time
                        ), block=False)
                else:
                    # Prevent CPU hogging when idle
                    time.sleep(0.001)
        
        except Exception as e:
            print(f"Error in process frames: {e}")
    
    def _detect_hands(self, frame):
        """Efficiently detect hands using MediaPipe"""
        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Optimize for performance
        image_rgb.flags.writeable = False
        results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True
        
        # Convert back to BGR for display
        processed_frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Initialize hands data
        hands_data = {
            "left_hand": None,
            "right_hand": None
        }
        
        # Extract hand landmarks if detected
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness
                handedness = results.multi_handedness[idx].classification[0].label
                
                # Extract landmark positions
                landmarks_3d = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
                
                # Store by handedness
                hand_key = "left_hand" if handedness == "Left" else "right_hand"
                hands_data[hand_key] = landmarks_3d
                
                # Draw landmarks and connections
                mp_drawing.draw_landmarks(
                    processed_frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        
        return processed_frame, hands_data
    
    def _filter_hand_positions(self, hands_data):
        """Apply exponential filtering to reduce jitter"""
        filtered_data = hands_data.copy()
        
        for hand_type in ["left_hand", "right_hand"]:
            if hands_data[hand_type] is not None:
                # Update history
                self.position_history[hand_type].pop(0)
                self.position_history[hand_type].append(hands_data[hand_type])
                
                # Only filter if we have history
                valid_history = [p for p in self.position_history[hand_type] if p is not None]
                if len(valid_history) > 1:
                    # Exponential weights (more recent = higher weight)
                    weights = np.exp(np.linspace(-1, 0, len(valid_history)))
                    weights /= weights.sum()
                    
                    # Apply weighted average
                    filtered_position = np.zeros_like(valid_history[0])
                    for i, pos in enumerate(valid_history):
                        filtered_position += pos * weights[i]
                    
                    filtered_data[hand_type] = filtered_position
        
        return filtered_data
    
    def _display_frame(self, processed_data):
        """Display the processed frame with pinch and performance info"""
        processed_frame, hands_data, detected_keys, avg_fps, processing_time = processed_data
        
        # Show pinch threshold
        cv2.putText(
            processed_frame,
            f"Pinch Threshold: {config.PINCH_THRESHOLD:.3f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            config.TEXT_COLOR,
            2
        )
        
        # Show performance metrics
        cv2.putText(
            processed_frame,
            f"FPS: {avg_fps:.1f} | Process: {processing_time*1000:.1f}ms",
            (10, processed_frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            config.TEXT_COLOR,
            1
        )
        
        # Add quit instructions
        cv2.putText(
            processed_frame,
            "Press 'q' to quit",
            (processed_frame.shape[1] - 150, processed_frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Display the frame
        cv2.imshow("Hand Keyboard", processed_frame)

class FPSTracker:
    """Simple FPS tracker with rolling average"""
    def __init__(self, max_samples=30):
        self.fps_values = []
        self.max_samples = max_samples
        
    def update(self, new_fps):
        self.fps_values.append(new_fps)
        if len(self.fps_values) > self.max_samples:
            self.fps_values.pop(0)
            
    def get_avg_fps(self):
        return sum(self.fps_values) / len(self.fps_values) if self.fps_values else 0

def main():
    """Main function to run the hand keyboard"""
    try:
        # Get camera selection
        camera_index = int(input("Enter camera index (0 for built-in, typically 1 for Continuity Camera): ") or "0")
        
        # Create and start hand keyboard
        keyboard = HandKeyboard(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            camera_index=camera_index
        )
        
        print("Starting Hand Keyboard. Press 'q' to quit.")
        print(f"Current pinch threshold: {config.PINCH_THRESHOLD}")
        print("To change sensitivity, edit PINCH_THRESHOLD in config.py")
        keyboard.start()
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Stopping Hand Keyboard")
        if 'keyboard' in locals():
            keyboard.stop()

if __name__ == "__main__":
    main()