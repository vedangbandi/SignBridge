"""
Real-time prediction module
"""
import numpy as np
from typing import Optional, Tuple, List
from collections import deque
from model.model_builder import ModelBuilder
from utils.config import (
    SEQUENCE_LENGTH,
    PREDICTION_CONFIDENCE_THRESHOLD,
    PREDICTION_CONSISTENCY_FRAMES,
    DEFAULT_MODEL_PATH
)
from utils.logger import app_logger


class Predictor:
    """Handles real-time sign language prediction."""
    
    def __init__(self):
        """Initialize predictor."""
        self.model = None
        self.labels = []
        self.sequence = deque(maxlen=SEQUENCE_LENGTH)
        self.predictions = deque(maxlen=PREDICTION_CONSISTENCY_FRAMES)
        self.current_prediction = None
        self.current_confidence = 0.0
    
    def load_model(self, model_path: str = DEFAULT_MODEL_PATH, labels: List[str] = None) -> bool:
        """
        Load trained model.
        
        Args:
            model_path: Path to model file
            labels: List of label names
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.model = ModelBuilder.load_model(model_path)
            if self.model is None:
                return False
            
            if labels:
                self.labels = labels
                app_logger.info(f"Model loaded with {len(labels)} labels: {labels}")
            else:
                app_logger.warning("No labels provided, predictions will be indices")
            
            # Reset state
            self.reset()
            return True
            
        except Exception as e:
            app_logger.error(f"Error loading model: {e}")
            return False
    
    def reset(self):
        """Reset prediction state."""
        self.sequence.clear()
        self.predictions.clear()
        self.current_prediction = None
        self.current_confidence = 0.0
    
    def add_keypoints(self, keypoints: np.ndarray):
        """
        Add keypoints to sequence buffer.
        
        Args:
            keypoints: Keypoint array of shape (63,)
        """
        self.sequence.append(keypoints)
    
    def predict(self, keypoints: np.ndarray,
                threshold: float = PREDICTION_CONFIDENCE_THRESHOLD) -> Tuple[Optional[str], float]:
        """
        Make prediction on current sequence.
        
        Args:
            keypoints: Current frame keypoints
            threshold: Confidence threshold for predictions
            
        Returns:
            Tuple of (predicted_label, confidence)
        """
        if self.model is None:
            return None, 0.0
        
        # Add keypoints to sequence
        self.add_keypoints(keypoints)
        
        # Need full sequence to predict
        if len(self.sequence) < SEQUENCE_LENGTH:
            return None, 0.0
        
        try:
            # Prepare sequence for prediction
            sequence_array = np.array(list(self.sequence))
            sequence_input = np.expand_dims(sequence_array, axis=0)
            
            # Make prediction
            prediction_probs = self.model.predict(sequence_input, verbose=0)[0]
            predicted_idx = np.argmax(prediction_probs)
            confidence = prediction_probs[predicted_idx]
            
            # Add to predictions buffer
            self.predictions.append(predicted_idx)
            
            # Check consistency and confidence
            if len(self.predictions) >= PREDICTION_CONSISTENCY_FRAMES:
                # Check if last N predictions are consistent
                recent_predictions = list(self.predictions)
                unique_predictions = np.unique(recent_predictions)
                
                if len(unique_predictions) == 1 and confidence > threshold:
                    # Consistent prediction with high confidence
                    label = self.labels[predicted_idx] if predicted_idx < len(self.labels) else str(predicted_idx)
                    self.current_prediction = label
                    self.current_confidence = confidence
                    return label, confidence
            
            return None, confidence
            
        except Exception as e:
            app_logger.error(f"Prediction error: {e}")
            return None, 0.0
    
    def get_current_prediction(self) -> Tuple[Optional[str], float]:
        """
        Get current stable prediction.
        
        Returns:
            Tuple of (predicted_label, confidence)
        """
        return self.current_prediction, self.current_confidence
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def get_label_count(self) -> int:
        """Get number of labels."""
        return len(self.labels)
