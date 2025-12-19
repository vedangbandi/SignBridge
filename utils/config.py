"""
Configuration settings for Sign Language Recognition System
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dataset_dir = os.path.join(BASE_DIR, "dataset")

def set_dataset_dir(path):
    global _dataset_dir
    _dataset_dir = path
    os.makedirs(_dataset_dir, exist_ok=True)

@property
def DATASET_DIR():
    return _dataset_dir

# Use a standard variable for compatibility
DATASET_DIR = _dataset_dir # This will be the initial value
DATASET_PATH = DATASET_DIR  # Alias for consistency

def update_dataset_path(new_path):
    global DATASET_DIR, DATASET_PATH
    DATASET_DIR = new_path
    DATASET_PATH = new_path
    os.makedirs(DATASET_DIR, exist_ok=True)

# Ensure initial directories exist
MODEL_DIR = os.path.join(BASE_DIR, "model")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Model settings
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, "model.h5")
MODEL_JSON_PATH = os.path.join(MODEL_DIR, "model.json")
DEFAULT_LABELS_PATH = os.path.join(MODEL_DIR, "labels.txt")

# Training defaults
DEFAULT_EPOCHS = 50
DEFAULT_BATCH_SIZE = 32
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_VALIDATION_SPLIT = 0.2
SEQUENCE_LENGTH = 30  # Number of frames per sequence
KEYPOINTS_PER_FRAME = 63  # 21 hand landmarks * 3 coordinates (x, y, z)

# Data capture settings
DEFAULT_CAPTURE_COUNT = 30
CAPTURE_FPS = 30
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# MediaPipe settings
MP_MIN_DETECTION_CONFIDENCE = 0.5
MP_MIN_TRACKING_CONFIDENCE = 0.5
MP_MODEL_COMPLEXITY = 0
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm
]

# Prediction settings
PREDICTION_CONFIDENCE_THRESHOLD = 0.8
PREDICTION_CONSISTENCY_FRAMES = 3

# UI settings
WINDOW_TITLE = "SignBridge: Bridging Sign Language and Trainable Hand Gestures"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 850
THEME_COLOR = "#2C3E50"
ACCENT_COLOR = "#3498DB"
SUCCESS_COLOR = "#27AE60"
ERROR_COLOR = "#E74C3C"
WARNING_COLOR = "#F39C12"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
