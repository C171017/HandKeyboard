import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import queue
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# MediaPipe solutions
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class HandTracker:
    def __init__(self, 
                 static_image_mode=False,
                 max_num_hands=2,
                 model_complexity=1,
                 min_detection_confidence=0.6,
                 min_tracking_confidence=0.6,
                 enable_3d_visualization=True):
        """
        Initialize the hand tracker optimized for 3D accuracy on Apple Silicon.
        """
        # Initialize parameters
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.enable_3d_visualization = enable_3d_visualization
        
        # Initialize queues for threading
        self.input_queue = queue.Queue(maxsize=5)
        self.output_queue = queue.Queue(maxsize=5)
        
        # Position history for filtering (reduces jitter)
        self.position_history = {
            "left_hand": [None] * 5,
            "right_hand": [None] * 5
        }
        
        # Initialize camera and dimensions
        self.cap = None
        self.frame_width = 640  # Optimal for M4 Max balance
        self.frame_height = 480  # Optimal for M4 Max balance
        
        # Initialize MediaPipe hands detector
        self.hands = None
        
        # Initialize threads
        self.processing_thread = None
        self.running = False
        
        # Performance metrics
        self.fps_counter = []
        self.detection_times = []
        
        # 3D visualization
        self.fig = None
        self.ax = None
        if self.enable_3d_visualization:
            self._setup_3d_visualization()
    
    def _setup_3d_visualization(self):
        """Setup 3D visualization window"""
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Hand Landmarks')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_zlim(-0.5, 0.5)
        plt.ion()  # Interactive mode on
        plt.show(block=False)
    
    def start(self):
        """Start the hand tracking system"""
        # Initialize the webcam
        self.cap = cv2.VideoCapture(0)
        
        # Apple M4 Max optimizations
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Try hardware acceleration for Apple Silicon
        try:
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, 1)
        except:
            pass
        
        # Initialize MediaPipe hands with parameters prioritizing accuracy
        self.hands = mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_num_hands,
            model_complexity=self.model_complexity,  # Higher for better 3D accuracy
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence)
        
        # Start the processing thread
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_frames)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Run the main capturing loop
        self._capture_frames()
    
    def stop(self):
        """Stop the hand tracking system"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        plt.close('all')
    
    def _capture_frames(self):
        """Capture frames from the webcam in a separate thread"""
        try:
            while self.running and self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read from webcam")
                    break
                
                # Add frame to input queue
                if not self.input_queue.full():
                    self.input_queue.put((frame, time.time()), block=False)
                
                # Get processed frame from output queue
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
        """Process frames to detect hands in a separate thread"""
        try:
            while self.running:
                if not self.input_queue.empty():
                    frame, timestamp = self.input_queue.get(block=False)
                    
                    # Start timer for processing time measurement
                    start_time = time.time()
                    
                    # Process the frame to detect hands
                    processed_frame, hands_data = self._detect_hands(frame)
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    self.detection_times.append(processing_time)
                    if len(self.detection_times) > 30:
                        self.detection_times.pop(0)
                    
                    # Filter 3D positions for stability
                    filtered_hands_data = self._filter_3d_positions(hands_data)
                    
                    # Calculate metrics based on hand positions
                    metrics = self._calculate_hand_metrics(filtered_hands_data)
                    
                    # Calculate FPS
                    current_time = time.time()
                    fps = 1 / (current_time - timestamp) if (current_time - timestamp) > 0 else 0
                    self.fps_counter.append(fps)
                    if len(self.fps_counter) > 30:
                        self.fps_counter.pop(0)
                    avg_fps = sum(self.fps_counter) / len(self.fps_counter) if self.fps_counter else 0
                    
                    # Put processed data in output queue
                    if not self.output_queue.full():
                        self.output_queue.put((
                            processed_frame, 
                            filtered_hands_data, 
                            metrics, 
                            avg_fps,
                            sum(self.detection_times) / len(self.detection_times) if self.detection_times else 0
                        ), block=False)
                else:
                    # Sleep briefly to prevent CPU hogging when queue is empty
                    time.sleep(0.001)
        
        except Exception as e:
            print(f"Error in process frames: {e}")
    
    def _detect_hands(self, frame):
        """Detect hands and extract 3D positions"""
        # Convert to RGB (MediaPipe requires RGB)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # To improve performance, mark image as not writeable
        image_rgb.flags.writeable = False
        
        # Process the image and detect hands
        results = self.hands.process(image_rgb)
        
        # Mark the image as writeable again for drawing
        image_rgb.flags.writeable = True
        
        # Convert back to BGR for OpenCV
        processed_frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Initialize hands data dictionary
        hands_data = {
            "left_hand": None,
            "right_hand": None,
            "num_hands_detected": 0,
            "handedness": []
        }
        
        # Check if hands are detected
        if results.multi_hand_landmarks:
            hands_data["num_hands_detected"] = len(results.multi_hand_landmarks)
            
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness (left or right)
                handedness = results.multi_handedness[idx].classification[0].label
                confidence = results.multi_handedness[idx].classification[0].score
                hands_data["handedness"].append((handedness, confidence))
                
                # Extract 3D landmarks
                landmarks_3d = []
                for landmark in hand_landmarks.landmark:
                    landmarks_3d.append([landmark.x, landmark.y, landmark.z])
                
                # Store 3D positions based on handedness
                if handedness == "Left":
                    hands_data["left_hand"] = np.array(landmarks_3d)
                else:
                    hands_data["right_hand"] = np.array(landmarks_3d)
                
                # Draw hand landmarks on the frame
                mp_drawing.draw_landmarks(
                    processed_frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Annotate handedness with confidence
                h, w, _ = processed_frame.shape
                cv2.putText(processed_frame, 
                          f"{handedness} Hand ({confidence:.2f})", 
                          (int(hand_landmarks.landmark[0].x * w), 
                           int(hand_landmarks.landmark[0].y * h - 20)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return processed_frame, hands_data
    
    def _filter_3d_positions(self, hands_data):
        """Filter 3D hand positions to reduce jitter"""
        # Update position history
        for hand_type in ["left_hand", "right_hand"]:
            if hands_data[hand_type] is not None:
                # Shift history and add new position
                self.position_history[hand_type].pop(0)
                self.position_history[hand_type].append(hands_data[hand_type])
            
        # Create filtered copy of hands_data
        filtered_hands_data = hands_data.copy()
        
        # Apply filtering for each hand if enough history is available
        for hand_type in ["left_hand", "right_hand"]:
            valid_positions = [pos for pos in self.position_history[hand_type] if pos is not None]
            if valid_positions and hands_data[hand_type] is not None:
                # Apply exponential moving average (more weight to recent positions)
                weights = np.exp(np.linspace(-1, 0, len(valid_positions)))
                weights = weights / np.sum(weights)
                
                filtered_position = np.zeros_like(valid_positions[0])
                for i, pos in enumerate(valid_positions):
                    filtered_position += pos * weights[i]
                
                filtered_hands_data[hand_type] = filtered_position
        
        return filtered_hands_data
    
    def _calculate_hand_metrics(self, hands_data):
        """Calculate 3D metrics from hand positions"""
        metrics = {}
        
        # Calculate metrics if both hands are detected
        if hands_data["left_hand"] is not None and hands_data["right_hand"] is not None:
            # Wrist positions (landmark 0)
            left_wrist = hands_data["left_hand"][0]
            right_wrist = hands_data["right_hand"][0]
            
            # Calculate Euclidean distance in 3D space
            wrist_distance_3d = np.linalg.norm(left_wrist - right_wrist)
            metrics["wrist_distance_3d"] = wrist_distance_3d
            
            # Calculate hand openness (average distance from wrist to fingertips)
            left_fingertips = [4, 8, 12, 16, 20]  # Indices of fingertips
            right_fingertips = [4, 8, 12, 16, 20]
            
            left_openness = np.mean([np.linalg.norm(hands_data["left_hand"][i] - left_wrist) for i in left_fingertips])
            right_openness = np.mean([np.linalg.norm(hands_data["right_hand"][i] - right_wrist) for i in right_fingertips])
            
            metrics["left_hand_openness"] = left_openness
            metrics["right_hand_openness"] = right_openness
        
        return metrics
    
    def _display_frame(self, processed_data):
        """Display the processed frame and 3D visualization"""
        processed_frame, hands_data, metrics, avg_fps, avg_detection_time = processed_data
        
        # Display metrics on the frame
        y_offset = 30
        for metric_name, value in metrics.items():
            cv2.putText(
                processed_frame,
                f"{metric_name}: {value:.4f}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            y_offset += 30
        
        # Display performance metrics
        cv2.putText(
            processed_frame,
            f"FPS: {avg_fps:.2f}, Detection: {avg_detection_time*1000:.1f}ms",
            (10, processed_frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        # Display the frame
        cv2.imshow("MediaPipe 3D Hand Tracking", processed_frame)
        
        # Update 3D visualization if enabled
        if self.enable_3d_visualization and (hands_data["left_hand"] is not None or hands_data["right_hand"] is not None):
            self._update_3d_visualization(hands_data)
    
    def _update_3d_visualization(self, hands_data):
        """Update the 3D visualization with current hand positions"""
        # Clear previous plot
        self.ax.clear()
        
        # Set fixed scale for better visualization
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_zlim(-0.5, 0.5)
        
        # Set labels and title
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Hand Landmarks')
        
        # Plot each hand if detected
        colors = {'left_hand': 'b', 'right_hand': 'r'}
        for hand_type in ["left_hand", "right_hand"]:
            if hands_data[hand_type] is not None:
                # Extract coordinates
                xs = hands_data[hand_type][:, 0]
                ys = hands_data[hand_type][:, 1]
                zs = hands_data[hand_type][:, 2]
                
                # Plot landmarks
                self.ax.scatter(xs, ys, zs, c=colors[hand_type], marker='o')
                
                # Connect landmarks according to hand connections
                for connection in mp_hands.HAND_CONNECTIONS:
                    self.ax.plot(
                        [xs[connection[0]], xs[connection[1]]],
                        [ys[connection[0]], ys[connection[1]]],
                        [zs[connection[0]], zs[connection[1]]],
                        c=colors[hand_type]
                    )
        
        # Update the plot
        plt.draw()
        plt.pause(0.001)

def main():
    """Main function to run the optimized 3D hand tracker"""
    try:
        # Create and start hand tracker - parameters optimized for M4 Max
        tracker = HandTracker(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,  # 1 is good balance for M4 Max (0=fast, 2=accurate)
            min_detection_confidence=0.6,  # Higher = more accurate but slower
            min_tracking_confidence=0.6,   # Higher = more stable tracking
            enable_3d_visualization=True   # Show 3D visualization
        )
        
        print("Starting hand tracker. Press 'q' to quit.")
        tracker.start()
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Stopping hand tracker")
        if 'tracker' in locals():
            tracker.stop()

if __name__ == "__main__":
    main()