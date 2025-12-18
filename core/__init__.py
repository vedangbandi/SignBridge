"""
Core package initialization
"""
from .image_capture import ImageCapture
from .dataset_manager import DatasetManager
from .label_manager import LabelManager
from .trainer import Trainer
from .predictor import Predictor

__all__ = [
    'ImageCapture',
    'DatasetManager',
    'LabelManager',
    'Trainer',
    'Predictor'
]
