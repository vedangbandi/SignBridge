"""
Image capture and keypoint extraction module
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple
from utils.config import (
    MP_MIN_DETECTION_CONFIDENCE,
    MP_MIN_TRACKING_CONFIDENCE,
    MP_MODEL_COMPLEXITY,
    KEYPOINTS_PER_FRAME
)
from utils.logger import app_logger


class ImageCapture:
    """Handles webcam capture and MediaPipe hand detection."""
    
    def __init__(self):
        """Initialize image capture with MediaPipe."""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = None
        self.cap = None
        
    def start_capture(self, camera_index: int = 0) -> bool:
        """
        Start webcam capture.
        
        Args:
            camera_index: Camera device index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                app_logger.error(f"Failed to open camera {camera_index}")
                return False
            
            # Initialize MediaPipe Hands
            self.hands = self.mp_hands.Hands(
                model_complexity=MP_MODEL_COMPLEXITY,
                min_detection_confidence=MP_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=MP_MIN_TRACKING_CONFIDENCE
            )
            
            app_logger.info(f"Camera {camera_index} started successfully")
            return True
        except Exception as e:
            app_logger.error(f"Error starting capture: {e}")
            return False
    
    def stop_capture(self):
        """Stop webcam capture and release resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.hands:
            self.hands.close()
            self.hands = None
        app_logger.info("Camera stopped")
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the webcam.
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.cap:
            return False, None
        
        ret, frame = self.cap.read()
        return ret, frame
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[object]]:
        """
        Process frame with MediaPipe to detect hands.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Tuple of (processed_frame, results)
        """
        if not self.hands:
            return frame, None
        
        # Convert BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process with MediaPipe
        results = self.hands.process(image)
        
        # Convert back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        return image, results
    
    def extract_keypoints(self, results: object) -> Optional[np.ndarray]:
        """
        Extract hand keypoints from MediaPipe results.
        
        Args:
            results: MediaPipe results object
            
        Returns:
            Numpy array of shape (63,) with hand keypoints, or None if no hand detected
        """
        if results and results.multi_hand_landmarks:
            # Get first hand
            hand = results.multi_hand_landmarks[0]
            
            # Extract x, y, z coordinates for all 21 landmarks
            keypoints = []
            for landmark in hand.landmark:
                keypoints.extend([landmark.x, landmark.y, landmark.z])
            
            return np.array(keypoints)
        else:
            # Return zeros if no hand detected
            return np.zeros(KEYPOINTS_PER_FRAME)
    
    def draw_landmarks(self, frame: np.ndarray, results: object) -> np.ndarray:
        """
        Draw hand landmarks on frame.
        
        Args:
            frame: Input frame
            results: MediaPipe results
            
        Returns:
            Frame with landmarks drawn
        """
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
        return frame
    
    def capture_sequence(self, num_frames: int = 30, draw_landmarks: bool = True) -> Tuple[list, list]:
        """
        Capture a sequence of frames and extract keypoints.
        
        Args:
            num_frames: Number of frames to capture
            draw_landmarks: Whether to draw landmarks on frames
            
        Returns:
            Tuple of (frames_list, keypoints_list)
        """
        frames = []
        keypoints_list = []
        
        for i in range(num_frames):
            ret, frame = self.read_frame()
            if not ret:
                app_logger.warning(f"Failed to read frame {i}")
                break
            
            # Process frame
            processed_frame, results = self.process_frame(frame)
            
            # Extract keypoints
            keypoints = self.extract_keypoints(results)
            keypoints_list.append(keypoints)
            
            # Draw landmarks if requested
            if draw_landmarks:
                processed_frame = self.draw_landmarks(processed_frame, results)
            
            frames.append(processed_frame)
        
        return frames, keypoints_list
    
    def is_capturing(self) -> bool:
        """Check if capture is active."""
        return self.cap is not None and self.cap.isOpened()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop_capture()
