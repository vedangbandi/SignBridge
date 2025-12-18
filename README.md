# SignBridge: Bridging Sign Language and Trainable Hand Gestures

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt-5-green?style=for-the-badge&logo=qt)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-orange?style=for-the-badge&logo=tensorflow)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.8-red?style=for-the-badge)

**A unified, professional GUI application for dataset creation, training, and real-time sign language recognition.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Project Structure](#-project-structure)

</div>

---

## 🚀 Overview

**SignBridge** is a complete refactor of the original project into a modular, object-oriented application with a modern graphical user interface (GUI). It streamlines the entire workflow of building a gesture recognition system into a single application.

---

## ✨ Key Features

### 1. 📸 Dataset Creator
- **Live Camera Feed**: Preview your webcam stream in real-time.
- **Dynamic Class Creation**: Add new gesture labels (e.g., "Hello", "Yes") on the fly.
- **Automated Capture**: Capture consistent sequences of hand landmarks (30 frames per sequence).
- **Progress Tracking**: Visual progress bar for data collection.

### 2. 📁 Dataset Browser
- **Visual Management**: View all captured labels and sequences.
- **Easy Editing**: Rename labels or delete specific sequences with a click.
- **Statistics**: View total dataset size and balance.

### 3. 🎓 Integrated Training
- **Customizable**: Set epochs, batch size, and learning rate from the GUI.
- **Real-Time Visualization**: Watch live accuracy and loss graphs during training.
- **Threaded Execution**: UI remains responsive while the model trains in the background.

### 4. 🔮 Real-Time Prediction
- **Live Recognition**: Instantly recognize trained gestures.
- **Confidence Scoring**: See the model's confidence for every prediction.
- **Threshold Control**: Adjust sensitivity with a slider.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Webcam

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

### Step 1: Create a Dataset
1. Go to the **Dataset Creator** tab.
2. Enter a label name (e.g., "A").
3. Click **Start Camera**.
4. Position your hand and click **Start Capture**.
5. The system will auto-capture 30 sequences. Move your hand slightly between sequences for better generalization.

### Step 2: Inspection (Optional)
1. Go to the **Dataset Browser** tab.
2. Verify that your labels and sequences are correct.
3. Delete any bad data if necessary.

### Step 3: Train the Model
1. Go to the **Training** tab.
2. Click **Validate Dataset** to ensure you have enough data.
3. Click **Start Training**.
4. Wait for the process to finish (accuracy usually reaches >95%).

### Step 4: Real-Time Prediction
1. Go to the **Prediction** tab.
2. Click **Load Model** (the system loads the newly trained model automatically).
3. Click **Start Prediction**.
4. Test your gestures!

---

## 🏗️ Project Structure

```
Sign-Language-Recognition-System/
│
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
│
├── ui/                      # GUI Components
│   ├── main_window.py       # Main container
│   ├── dataset_tab.py       # Data capture UI
│   ├── train_tab.py         # Training UI
│   └── predict_tab.py       # Prediction UI
│
├── core/                    # Logic Modules
│   ├── image_capture.py     # MediaPipe handling
│   ├── dataset_manager.py   # Data I/O
│   ├── trainer.py           # Training loop
│   └── predictor.py         # Inference engine
│
├── dataset/                 # Data Storage
│   ├── A/                   # Gesture Folders
│   └── B/
│
├── model/                   # Model Storage
│   └── model.h5             # Trained Model
│
└── utils/                   # Helpers
    ├── config.py            # Settings
    └── logger.py            # Logging
```

---

## ⚠️ Troubleshooting

- **Camera not working?** Ensure no other app is using the webcam.
- **Low accuracy?** Try capturing more data (50+ sequences per label) with varied lighting and hand positions.
- **App freezes?** The app uses threading for heavy tasks, but initial model loading might take a few seconds.

---

**Original Code Refactored by Google DeepMind Agent**
