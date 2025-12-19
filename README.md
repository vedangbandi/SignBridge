# SignBridge: Bridging Sign Language and Trainable Hand Gestures

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt-5-green?style=for-the-badge&logo=qt)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-orange?style=for-the-badge&logo=tensorflow)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.8-red?style=for-the-badge)

**A unified, professional GUI application for dataset creation, training, and real-time sign language recognition.**


</div>

---

## 🚀 Overview

**SignBridge** is a complete, modular, object-oriented application with a modern graphical user interface (GUI). It streamlines the entire workflow of building a gesture recognition system—from raw image ingestion to real-time AI inference—into a single, high-performance application.

---

## ✨ Key Features

### 1. 📂 Optimized Dataset Browser & Sync
- **Dynamic Dataset Selection**: Browse and select any dataset directory at runtime.
- **30x Faster Loading**: Uses consolidated `keypoints.npy` storage to reduce disk I/O bottlenecks.
- **🔄 Sync & Repair Tool**: 
    - Automatically imports loose images (`.jpg`, `.png`) into the sequence structure.
    - Generates missing landmark data using MediaPipe with a real-time progress bar.
    - organizes external data folders for training readiness.

### 2. 📸 Dataset Creator
- **Live Camera Feed**: Preview your webcam stream in real-time.
- **Dynamic Class Creation**: Add new gesture labels (e.g., "Hello", "Ok") on the fly.
- **Automated Capture**: Capture consistent sequences of hand landmarks (30 frames per sequence).

### 3. 🎓 Professional Training Engine
- **Robust Model Architecture**: 
    - **Gaussian Noise**: Improved generalization for shaky hands.
    - **Batch Normalization**: Faster convergence and stable training.
    - **Class Weighting**: Automatically balances samples to prevent bias towards common labels (like "Ok").
- **Real-Time Visualization**: Live accuracy and loss graphs.
- **Validation Suite**: built-in dataset validator before training starts.

### 4. 🔮 High-Speed Real-Time Prediction
- **Zero-Latency Inference**: Optimized temporal buffer for instant recognition.
- **Adaptive Thresholding**: Adjust sensitivity and consistency frames on the fly.
- **High-DPI Support**: Crisp visuals on 4K and Retina displays.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Webcam

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vedangbandi/SignBridge.git
   cd Sign-Language-Recognition-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## 📖 Usage Guide

### Step 1: Manage Your Data
1. Go to the **Dataset Browser** tab.
2. Click **Browse Dataset** to select your working folder.
3. If you have loose images in a folder, click **🔄 Sync & Repair**. The app will automatically generate the required landmark files and organize your data.

### Step 2: Capture New Data (Optional)
1. Go to the **Dataset Creator** tab.
2. Enter a label name and click **Start Capture**.
3. Move your hand slightly to give the model better variety.

### Step 3: Train the Model
1. Go to the **Training** tab.
2. Adjust epochs (recommended: 50+) and batch size.
3. Click **Start Training**. The model now uses **Class Weighting** to ensure rare gestures are learned as well as common ones.

### Step 4: Real-Time Prediction
1. Go to the **Prediction** tab.
2. Click **Load Model** (automatically detects `labels.txt` and `model.h5`).
3. Click **Start Prediction**. The system is now optimized to predict every 2nd frame for maximum smoothness.

---

## 🏗️ Project Structure

```
SignBridge/
│
├── main.py                  # Entry point
├── create_exe.py            # PyInstaller build script
├── requirements.txt         # Dependencies
│
├── ui/                      # GUI Components (PyQt5)
│   ├── browser_tab.py       # Dataset management & Sync logic
│   ├── dataset_tab.py       # Data capture UI
│   ├── train_tab.py         # Training UI & Graphing
│   └── predict_tab.py       # Real-time inference UI
│
├── core/                    # Logic Modules
│   ├── image_capture.py     # MediaPipe Hand Tracking
│   ├── dataset_manager.py   # Multi-threaded Data Loading
│   ├── trainer.py           # Keras training with Class Weighting
│   └── predictor.py         # Temporal inference engine
│
├── utils/                   # Shared Utilities
│   ├── file_ops.py          # Consolidated .npy operations
│   ├── config.py            # Global settings & constants
│   └── logger.py            # Application logging
```

---

## 📦 Building an Executable

To create a standalone windows executable:
```powershell
python create_exe.py
```
The build will be located in the `dist/SignBridge` folder.

---

## ⚠️ Troubleshooting

- **Model favoring one gesture?** Ensure your dataset is balanced, or use the new **Class Weighting** feature during training.
- **Slow predictions?** Ensure your camera FPS matches the `utils/config.py` settings (default 30 FPS).
- **Importing raw images?** Use the **Sync & Repair** button in the Browser tab to convert them to sequences.

---
