"""
File operations utilities
"""
import os
import shutil
import json
from typing import List, Dict, Optional
import numpy as np


def get_dataset_labels() -> List[str]:
    """
    Get all label names from dataset directory.
    
    Returns:
        List of label names (folder names in dataset directory)
    """
    from utils.config import DATASET_DIR
    
    if not os.path.exists(DATASET_DIR):
        return []
    
    labels = [
        d for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    ]
    return sorted(labels)


def get_label_path(label: str) -> str:
    """Get full path for a label directory."""
    from utils.config import DATASET_DIR
    return os.path.join(DATASET_DIR, label)


def create_label_directory(label: str) -> bool:
    """
    Create a new label directory.
    
    Args:
        label: Label name
        
    Returns:
        True if created successfully, False otherwise
    """
    try:
        label_path = get_label_path(label)
        os.makedirs(label_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating label directory: {e}")
        return False


def rename_label(old_label: str, new_label: str) -> bool:
    """
    Rename a label directory.
    
    Args:
        old_label: Current label name
        new_label: New label name
        
    Returns:
        True if renamed successfully, False otherwise
    """
    try:
        old_path = get_label_path(old_label)
        new_path = get_label_path(new_label)
        
        if not os.path.exists(old_path):
            return False
        
        if os.path.exists(new_path):
            return False
        
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        print(f"Error renaming label: {e}")
        return False


def delete_label(label: str) -> bool:
    """
    Delete a label directory and all its contents.
    
    Args:
        label: Label name
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        label_path = get_label_path(label)
        if os.path.exists(label_path):
            shutil.rmtree(label_path)
        return True
    except Exception as e:
        print(f"Error deleting label: {e}")
        return False


def get_label_sequences(label: str) -> List[str]:
    """
    Get all sequence directories for a label.
    
    Args:
        label: Label name
        
    Returns:
        List of sequence directory paths
    """
    label_path = get_label_path(label)
    if not os.path.exists(label_path):
        return []
    
    sequences = [
        os.path.join(label_path, d)
        for d in os.listdir(label_path)
        if os.path.isdir(os.path.join(label_path, d))
    ]
    return sorted(sequences)


def get_sequence_count(label: str) -> int:
    """Get number of sequences for a label."""
    return len(get_label_sequences(label))


def delete_sequence(label: str, sequence_idx: int) -> bool:
    """
    Delete a specific sequence.
    
    Args:
        label: Label name
        sequence_idx: Sequence index
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        sequence_path = os.path.join(get_label_path(label), str(sequence_idx))
        if os.path.exists(sequence_path):
            shutil.rmtree(sequence_path)
        return True
    except Exception as e:
        print(f"Error deleting sequence: {e}")
        return False


def get_dataset_stats() -> Dict:
    """
    Get statistics about the dataset.
    
    Returns:
        Dictionary with dataset statistics
    """
    labels = get_dataset_labels()
    stats = {
        'total_labels': len(labels),
        'labels': {},
        'total_sequences': 0
    }
    
    for label in labels:
        seq_count = get_sequence_count(label)
        stats['labels'][label] = seq_count
        stats['total_sequences'] += seq_count
    
    return stats


def save_json(data: dict, filepath: str) -> bool:
    """Save data to JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_json(filepath: str) -> Optional[dict]:
    """Load data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None


def save_sequence(label: str, sequence_idx: int, keypoints_sequence: List[np.ndarray]) -> bool:
    """
    Save a sequence of keypoints as a single numpy file for efficiency.
    """
    try:
        sequence_path = os.path.join(get_label_path(label), str(sequence_idx))
        os.makedirs(sequence_path, exist_ok=True)
        
        # Consolidate into one file
        data = np.array(keypoints_sequence)
        file_path = os.path.join(sequence_path, "keypoints.npy")
        np.save(file_path, data)
        
        return True
    except Exception as e:
        print(f"Error saving sequence: {e}")
        return False


def load_sequence(label: str, sequence_idx: int, sequence_length: int = 30) -> Optional[np.ndarray]:
    """
    Load a sequence of keypoints. Prioritizes the consolidated 'keypoints.npy'.
    """
    try:
        sequence_path = os.path.join(get_label_path(label), str(sequence_idx))
        if not os.path.exists(sequence_path):
            return None
        
        # 1. Try modern consolidated file
        fast_path = os.path.join(sequence_path, "keypoints.npy")
        if os.path.exists(fast_path):
            return np.load(fast_path)
            
        # 2. Backward compatibility: load frame-by-frame
        frames = []
        found_any = False
        for frame_idx in range(sequence_length):
            frame_path = os.path.join(sequence_path, f"{frame_idx}.npy")
            if os.path.exists(frame_path):
                frames.append(np.load(frame_path))
                found_any = True
            else:
                frames.append(np.zeros(63))
        
        if not found_any: return None
        
        # Auto-consolidate for future loads
        arr = np.array(frames)
        try: np.save(fast_path, arr)
        except: pass
        
        return arr
    except Exception as e:
        print(f"Error loading sequence: {e}")
        return None


def save_preview_image(label: str, sequence_idx: int, image: np.ndarray) -> bool:
    """
    Save a preview image for a sequence.
    
    Args:
        label: Label name
        sequence_idx: Sequence index
        image: Image array (BGR)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        import cv2
        sequence_path = os.path.join(get_label_path(label), str(sequence_idx))
        os.makedirs(sequence_path, exist_ok=True)
        
        # Resize for thumbnail (lightweight)
        if image is not None and image.size > 0:
            thumbnail = cv2.resize(image, (320, 240))
            image_path = os.path.join(sequence_path, "preview.jpg")
            # Save with compression (quality 80)
            cv2.imwrite(image_path, thumbnail, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            return True
        return False
    except Exception as e:
        print(f"Error saving preview image: {e}")
        return False
