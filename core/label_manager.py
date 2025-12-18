"""
Label management module
"""
from typing import List, Dict
from utils.file_ops import (
    get_dataset_labels,
    rename_label,
    delete_label,
    get_sequence_count
)
from utils.logger import app_logger


class LabelManager:
    """Manages dataset labels."""
    
    def __init__(self):
        """Initialize label manager."""
        self.refresh()
    
    def refresh(self):
        """Refresh labels from dataset."""
        self.labels = get_dataset_labels()
    
    def get_all_labels(self) -> List[str]:
        """Get all labels."""
        return self.labels
    
    def rename(self, old_label: str, new_label: str) -> bool:
        """
        Rename a label.
        
        Args:
            old_label: Current label name
            new_label: New label name
            
        Returns:
            True if successful, False otherwise
        """
        if rename_label(old_label, new_label):
            self.refresh()
            app_logger.info(f"Renamed label '{old_label}' to '{new_label}'")
            return True
        return False
    
    def delete(self, label: str) -> bool:
        """
        Delete a label and all its data.
        
        Args:
            label: Label name
            
        Returns:
            True if successful, False otherwise
        """
        if delete_label(label):
            self.refresh()
            app_logger.info(f"Deleted label '{label}'")
            return True
        return False
    
    def get_label_info(self, label: str) -> Dict:
        """
        Get information about a label.
        
        Args:
            label: Label name
            
        Returns:
            Dictionary with label information
        """
        return {
            'name': label,
            'sequence_count': get_sequence_count(label)
        }
    
    def get_all_labels_info(self) -> List[Dict]:
        """
        Get information about all labels.
        
        Returns:
            List of dictionaries with label information
        """
        return [self.get_label_info(label) for label in self.labels]
