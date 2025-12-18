"""
UI package initialization
"""
from .main_window import MainWindow
from .dataset_tab import DatasetTab
from .browser_tab import BrowserTab
from .train_tab import TrainTab
from .predict_tab import PredictTab

__all__ = [
    'MainWindow',
    'DatasetTab',
    'BrowserTab',
    'TrainTab',
    'PredictTab'
]
