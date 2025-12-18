"""
Model training module
"""
import numpy as np
from typing import Optional, Callable
from model.model_builder import ModelBuilder
from utils.config import (
    DEFAULT_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
    DEFAULT_VALIDATION_SPLIT,
    DEFAULT_MODEL_PATH
)
from utils.logger import training_logger


class Trainer:
    """Handles model training."""
    
    def __init__(self):
        """Initialize trainer."""
        self.model = None
        self.labels = []
        self.is_training = False
        self.training_history = None
    
    def prepare_data(self, X: np.ndarray, y: np.ndarray, labels: list,
                    validation_split: float = DEFAULT_VALIDATION_SPLIT):
        """
        Prepare data for training.
        
        Args:
            X: Input data of shape (num_samples, sequence_length, keypoints)
            y: Label indices
            labels: List of label names
            validation_split: Fraction of data to use for validation
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Lazy load
        from sklearn.model_selection import train_test_split
        from keras.utils import to_categorical

        self.labels = labels
        num_classes = len(labels)
        
        # Convert labels to categorical
        y_categorical = to_categorical(y, num_classes=num_classes)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_categorical,
            test_size=validation_split,
            random_state=42,
            stratify=y
        )
        
        training_logger.info(f"Data prepared: {X_train.shape[0]} training, {X_test.shape[0]} validation samples")
        return X_train, X_test, y_train, y_test
    
    def train(self,
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: np.ndarray,
              y_val: np.ndarray,
              epochs: int = DEFAULT_EPOCHS,
              batch_size: int = DEFAULT_BATCH_SIZE,
              learning_rate: float = DEFAULT_LEARNING_RATE,
              progress_callback: Optional[Callable] = None) -> bool:
        """
        Train the model.
        
        Args:
            X_train: Training data
            y_train: Training labels
            X_val: Validation data
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size
            learning_rate: Learning rate
            progress_callback: Callback for progress updates
            
        Returns:
            True if training successful, False otherwise
        """
        try:
            # Lazy load
            from keras.callbacks import Callback
            
            # Define callback locally
            class TrainingCallback(Callback):
                def __init__(self, progress_cb):
                    super().__init__()
                    self.progress_cb = progress_cb
                
                def on_epoch_end(self, epoch, logs=None):
                    if self.progress_cb:
                        self.progress_cb(epoch, logs or {})

            self.is_training = True
            num_classes = y_train.shape[1]
            
            # Build model
            training_logger.info("Building model...")
            self.model = ModelBuilder.build_model(num_classes, learning_rate)
            
            # Log model summary
            summary = ModelBuilder.get_model_summary(self.model)
            training_logger.info(f"Model architecture:\n{summary}")
            
            # Create callback
            callback = TrainingCallback(progress_callback)
            
            # Train model
            training_logger.info(f"Starting training: {epochs} epochs, batch size {batch_size}")
            self.training_history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[callback],
                verbose=1
            )
            
            # Evaluate on validation set
            val_loss, val_acc = self.model.evaluate(X_val, y_val, verbose=0)
            training_logger.info(f"Training complete. Validation accuracy: {val_acc:.4f}")
            
            self.is_training = False
            return True
            
        except Exception as e:
            training_logger.error(f"Error during training: {e}")
            self.is_training = False
            return False
    
    def save_model(self, model_path: str = DEFAULT_MODEL_PATH) -> bool:
        """
        Save trained model.
        
        Args:
            model_path: Path to save model
            
        Returns:
            True if successful, False otherwise
        """
        if self.model is None:
            training_logger.warning("No model to save")
            return False
        
        return ModelBuilder.save_model(self.model, model_path)
    
    def get_training_history(self) -> Optional[dict]:
        """
        Get training history.
        
        Returns:
            Dictionary with training history or None
        """
        if self.training_history:
            return self.training_history.history
        return None
    
    def stop_training(self):
        """Stop training (if possible)."""
        self.is_training = False
        training_logger.info("Training stop requested")
