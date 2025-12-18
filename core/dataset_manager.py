"""
Dataset management module
"""
import os
import numpy as np
from typing import List, Dict, Tuple, Optional
from utils.file_ops import (
    get_dataset_labels,
    create_label_directory,
    save_sequence,
    load_sequence,
    get_sequence_count,
    delete_sequence,
    get_dataset_stats
)
from utils.config import SEQUENCE_LENGTH, KEYPOINTS_PER_FRAME
from utils.logger import app_logger


class DatasetManager:
    """Manages dataset operations including loading, saving, and statistics."""
    
    def __init__(self):
        """Initialize dataset manager."""
        self.labels = []
        self.refresh_labels()
    
    def refresh_labels(self):
        """Refresh the list of labels from dataset directory."""
        self.labels = get_dataset_labels()
        app_logger.info(f"Loaded {len(self.labels)} labels: {self.labels}")
    
    def get_labels(self) -> List[str]:
        """Get list of all labels."""
        return self.labels
    
    def add_label(self, label: str) -> bool:
        """
        Add a new label.
        
        Args:
            label: Label name
            
        Returns:
            True if successful, False otherwise
        """
        if label in self.labels:
            app_logger.warning(f"Label '{label}' already exists")
            return False
        
        if create_label_directory(label):
            self.refresh_labels()
            app_logger.info(f"Created new label: {label}")
            return True
        return False
    
    def save_captured_sequence(self, label: str, keypoints_sequence: List[np.ndarray], 
                             preview_image: Optional[np.ndarray] = None) -> bool:
        """
        Save a captured sequence of keypoints.
        """
        from utils.file_ops import save_sequence, save_preview_image
        
        # Get next sequence index
        sequence_idx = get_sequence_count(label)
        
        # Save sequence
        if save_sequence(label, sequence_idx, keypoints_sequence):
            # Save preview image if provided
            if preview_image is not None:
                save_preview_image(label, sequence_idx, preview_image)
                
            app_logger.info(f"Saved sequence {sequence_idx} for label '{label}'")
            return True
        return False
    
    def delete_label_sequence(self, label: str, sequence_idx: int) -> bool:
        """
        Delete a specific sequence.
        
        Args:
            label: Label name
            sequence_idx: Sequence index
            
        Returns:
            True if successful, False otherwise
        """
        if delete_sequence(label, sequence_idx):
            app_logger.info(f"Deleted sequence {sequence_idx} from label '{label}'")
            return True
        return False
    
    def get_stats(self) -> Dict:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary with dataset statistics
        """
        return get_dataset_stats()
    
    def load_all_data(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], List[str]]:
        """
        Load all dataset for training.
        
        Returns:
            Tuple of (X, y, labels) where:
                X: numpy array of shape (num_samples, sequence_length, keypoints_per_frame)
                y: numpy array of label indices
                labels: list of label names
        """
        self.refresh_labels()
        
        if not self.labels:
            app_logger.warning("No labels found in dataset")
            return None, None, []
        
        sequences = []
        label_indices = []
        
        # Create label to index mapping
        label_to_idx = {label: idx for idx, label in enumerate(self.labels)}
        
        # Load all sequences
        for label in self.labels:
            num_sequences = get_sequence_count(label)
            app_logger.info(f"Loading {num_sequences} sequences for label '{label}'")
            
            for seq_idx in range(num_sequences):
                sequence = load_sequence(label, seq_idx, SEQUENCE_LENGTH)
                if sequence is not None:
                    sequences.append(sequence)
                    label_indices.append(label_to_idx[label])
        
        if not sequences:
            app_logger.warning("No sequences loaded")
            return None, None, self.labels
        
        X = np.array(sequences)
        y = np.array(label_indices)
        
        app_logger.info(f"Loaded dataset: X shape {X.shape}, y shape {y.shape}")
        return X, y, self.labels
    
    def validate_dataset(self) -> Tuple[bool, str]:
        """
        Validate dataset for training.
        
        Returns:
            Tuple of (is_valid, message)
        """
        stats = self.get_stats()
        
        if stats['total_labels'] == 0:
            return False, "No labels found in dataset. Please create and capture data first."
        
        if stats['total_labels'] < 2:
            return False, "At least 2 labels are required for training."
        
        # Check if all labels have enough sequences
        min_sequences = 5
        for label, count in stats['labels'].items():
            if count < min_sequences:
                return False, f"Label '{label}' has only {count} sequences. Minimum {min_sequences} required."
        
        return True, f"Dataset is valid: {stats['total_labels']} labels, {stats['total_sequences']} total sequences"
    
    def get_label_count(self) -> int:
        """Get number of labels."""
        return len(self.labels)
    
    def get_total_sequences(self) -> int:
        """Get total number of sequences across all labels."""
        stats = self.get_stats()
        return stats['total_sequences']
