"""
Model building module
"""
from typing import Optional
import os
from utils.config import (
    SEQUENCE_LENGTH,
    KEYPOINTS_PER_FRAME,
    DEFAULT_LEARNING_RATE,
    DEFAULT_MODEL_PATH,
    MODEL_JSON_PATH
)
from utils.logger import training_logger


class ModelBuilder:
    """Builds and manages LSTM models for sign language recognition."""
    
    @staticmethod
    def build_model(num_classes: int, learning_rate: float = DEFAULT_LEARNING_RATE):
        """
        Build LSTM model for sign language recognition.
        """
        # Lazy load heavy dependencies
        from keras.models import Sequential
        from keras.layers import LSTM, Dense, Dropout, GaussianNoise, BatchNormalization
        from keras.optimizers import Adam
        from keras.regularizers import l2

        model = Sequential([
            # Input noise to handle shaky landmarks
            GaussianNoise(0.01, input_shape=(SEQUENCE_LENGTH, KEYPOINTS_PER_FRAME)),
            
            # First LSTM layer - Using default tanh for better sequence modeling
            LSTM(64, return_sequences=True),
            BatchNormalization(),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(128, return_sequences=True),
            BatchNormalization(),
            Dropout(0.2),
            
            # Third LSTM layer
            LSTM(64, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers with regularization
            Dense(128, activation='relu', kernel_regularizer=l2(0.001)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            
            # Output layer
            Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        optimizer = Adam(learning_rate=learning_rate)
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['categorical_accuracy']
        )
        
        training_logger.info(f"Built model with {num_classes} classes")
        training_logger.info(f"Model parameters: {model.count_params()}")
        
        return model
    
    @staticmethod
    def save_model(model, model_path: str = DEFAULT_MODEL_PATH) -> bool:
        """
        Save model to file.
        """
        try:
            # Save weights
            model.save(model_path)
            
            # Save architecture to JSON
            model_json = model.to_json()
            json_path = model_path.replace('.h5', '.json')
            with open(json_path, 'w') as f:
                f.write(model_json)
            
            training_logger.info(f"Model saved to {model_path}")
            return True
        except Exception as e:
            training_logger.error(f"Error saving model: {e}")
            return False
    
    @staticmethod
    def load_model(model_path: str = DEFAULT_MODEL_PATH):
        """
        Load model from file.
        """
        try:
            # Lazy load
            from tensorflow import keras
            
            if not os.path.exists(model_path):
                training_logger.warning(f"Model file not found: {model_path}")
                return None
            
            # Load model
            model = keras.models.load_model(model_path)
            training_logger.info(f"Model loaded from {model_path}")
            return model
        except Exception as e:
            training_logger.error(f"Error loading model: {e}")
            return None
    
    @staticmethod
    @staticmethod
    def get_model_summary(model) -> str:
        """
        Get model summary as string.
        
        Args:
            model: Keras model
            
        Returns:
            Model summary string
        """
        import io
        stream = io.StringIO()
        model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()
