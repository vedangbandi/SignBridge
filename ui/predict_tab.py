"""
Prediction Tab - GUI for real-time sign language prediction
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QFileDialog, QSlider
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import cv2
import numpy as np
from core.image_capture import ImageCapture
from core.predictor import Predictor
from core.dataset_manager import DatasetManager
from utils.config import DEFAULT_MODEL_PATH, PREDICTION_CONFIDENCE_THRESHOLD
from utils.logger import app_logger


class PredictTab(QWidget):
    """Prediction tab for real-time sign language recognition."""
    
    def __init__(self):
        super().__init__()
        self.capture = ImageCapture()
        self.predictor = Predictor()
        self.dataset_manager = DatasetManager()
        self.is_predicting = False
        self.init_ui()
        
        # Timer for prediction
        self.predict_timer = QTimer()
        self.predict_timer.timeout.connect(self.update_prediction)
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Real-Time Prediction")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # Model controls
        model_group = QGroupBox("Model")
        model_layout = QHBoxLayout()
        
        self.model_label = QLabel("No model loaded")
        self.model_label.setStyleSheet("color: #E74C3C;")
        model_layout.addWidget(self.model_label)
        
        load_model_btn = QPushButton("Load Model")
        load_model_btn.clicked.connect(self.load_model)
        load_model_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        model_layout.addWidget(load_model_btn)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Video preview
        preview_group = QGroupBox("Camera Feed")
        preview_layout = QVBoxLayout()
        preview_layout.setAlignment(Qt.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(640, 480)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #000; border: 2px solid #3498DB; border-radius: 4px;")
        self.preview_label.setText("Camera not started")
        preview_layout.addWidget(self.preview_label)
        
        # Camera controls
        camera_controls = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Prediction")
        self.start_btn.clicked.connect(self.toggle_prediction)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        camera_controls.addWidget(self.start_btn)
        
        preview_layout.addLayout(camera_controls)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Prediction result
        result_group = QGroupBox("Prediction Result")
        result_layout = QVBoxLayout()
        
        self.prediction_label = QLabel("No prediction")
        self.prediction_label.setAlignment(Qt.AlignCenter)
        self.prediction_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #2C3E50;
            padding: 20px;
            background-color: #ECF0F1;
            border-radius: 10px;
        """)
        result_layout.addWidget(self.prediction_label)
        
        self.confidence_label = QLabel("Confidence: 0%")
        self.confidence_label.setAlignment(Qt.AlignCenter)
        self.confidence_label.setStyleSheet("font-size: 18px; color: #7F8C8D;")
        result_layout.addWidget(self.confidence_label)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Confidence threshold
        threshold_group = QGroupBox("Settings")
        threshold_layout = QVBoxLayout()
        
        threshold_label_layout = QHBoxLayout()
        threshold_label_layout.addWidget(QLabel("Confidence Threshold:"))
        self.threshold_value_label = QLabel(f"{int(PREDICTION_CONFIDENCE_THRESHOLD * 100)}%")
        threshold_label_layout.addWidget(self.threshold_value_label)
        threshold_label_layout.addStretch()
        threshold_layout.addLayout(threshold_label_layout)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(50)
        self.threshold_slider.setMaximum(95)
        self.threshold_slider.setValue(int(PREDICTION_CONFIDENCE_THRESHOLD * 100))
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        threshold_layout.addWidget(self.threshold_slider)
        
        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("No predictions yet")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Prediction statistics
        self.prediction_count = 0
        self.correct_predictions = {}
    
    def load_model(self):
        """Load trained model."""
        # Try default model first
        labels = self.dataset_manager.get_labels()
        
        if not labels:
            QMessageBox.warning(
                self,
                "No Labels",
                "No labels found in dataset. Please create and train a model first."
            )
            return
        
        # Check if default model exists
        import os
        if os.path.exists(DEFAULT_MODEL_PATH):
            model_path = DEFAULT_MODEL_PATH
        else:
            # Ask user to select model
            model_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Model File",
                "",
                "Model Files (*.h5)"
            )
            
            if not model_path:
                return
        
        # Load model
        if self.predictor.load_model(model_path, labels):
            self.model_label.setText(f"Model loaded: {os.path.basename(model_path)}")
            self.model_label.setStyleSheet("color: #27AE60;")
            self.start_btn.setEnabled(True)
            QMessageBox.information(
                self,
                "Success",
                f"Model loaded successfully!\nRecognizes {len(labels)} gestures: {', '.join(labels)}"
            )
        else:
            QMessageBox.critical(self, "Error", "Failed to load model")
    
    def toggle_prediction(self):
        """Toggle prediction on/off."""
        if not self.is_predicting:
            # Start prediction
            if not self.predictor.is_model_loaded():
                QMessageBox.warning(self, "Warning", "Please load a model first")
                return
            
            if self.capture.start_capture():
                self.is_predicting = True
                self.predict_timer.start(30)  # ~33 FPS
                self.start_btn.setText("Stop Prediction")
                self.start_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        padding: 10px;
                        font-size: 14px;
                        font-weight: bold;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                self.predictor.reset()
                self.prediction_count = 0
                self.correct_predictions = {}
            else:
                QMessageBox.critical(self, "Error", "Failed to start camera")
        else:
            # Stop prediction
            self.predict_timer.stop()
            self.capture.stop_capture()
            self.is_predicting = False
            self.start_btn.setText("Start Prediction")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.preview_label.setText("Camera stopped")
    
    def update_prediction(self):
        """Update prediction from camera feed."""
        ret, frame = self.capture.read_frame()
        if not ret:
            return
        
        # Process frame
        processed_frame, results = self.capture.process_frame(frame)
        
        # Extract keypoints
        keypoints = self.capture.extract_keypoints(results)
        
        # Make prediction
        threshold = self.threshold_slider.value() / 100.0
        predicted_label, confidence = self.predictor.predict(keypoints, threshold)
        
        # Draw landmarks
        processed_frame = self.capture.draw_landmarks(processed_frame, results)
        
        # Draw prediction on frame
        if predicted_label:
            cv2.putText(
                processed_frame,
                f"{predicted_label}: {confidence:.2%}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                3
            )
            
            # Update prediction display
            self.prediction_label.setText(predicted_label)
            self.confidence_label.setText(f"Confidence: {confidence:.1%}")
            
            # Update statistics
            self.prediction_count += 1
            self.correct_predictions[predicted_label] = self.correct_predictions.get(predicted_label, 0) + 1
            self.update_stats()
        
        # Display frame
        self.display_frame(processed_frame)
    
    def display_frame(self, frame):
        """Display frame in preview label."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
    
    def on_threshold_changed(self, value):
        """Handle threshold slider change."""
        self.threshold_value_label.setText(f"{value}%")
    
    def update_stats(self):
        """Update prediction statistics."""
        if self.prediction_count == 0:
            self.stats_label.setText("No predictions yet")
            return
        
        stats_text = f"<b>Total Predictions:</b> {self.prediction_count}<br><br>"
        stats_text += "<b>Predictions by Gesture:</b><br>"
        
        for label, count in sorted(self.correct_predictions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.prediction_count) * 100
            stats_text += f"  • {label}: {count} ({percentage:.1f}%)<br>"
        
        self.stats_label.setText(stats_text)
    
    def cleanup(self):
        """Cleanup resources."""
        if self.is_predicting:
            self.predict_timer.stop()
            self.capture.stop_capture()
