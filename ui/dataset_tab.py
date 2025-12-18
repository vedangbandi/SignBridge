"""
Dataset Creator Tab - GUI for capturing training data
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QGroupBox, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from core.image_capture import ImageCapture
from core.dataset_manager import DatasetManager
from utils.config import DEFAULT_CAPTURE_COUNT, SEQUENCE_LENGTH
from utils.logger import app_logger


class CaptureWorker(QThread):
    """Worker thread for capturing sequences."""
    
    progress = pyqtSignal(int, int)  # current, total
    frame_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, capture: ImageCapture, label: str, num_sequences: int):
        super().__init__()
        self.capture = capture
        self.label = label
        self.num_sequences = num_sequences
        self.dataset_manager = DatasetManager()
        self.is_running = True
    
    def run(self):
        """Capture sequences."""
        try:
            for seq_idx in range(self.num_sequences):
                if not self.is_running:
                    self.finished.emit(False, "Capture cancelled")
                    return
                
                # Capture sequence
                frames, keypoints_list = self.capture.capture_sequence(
                    num_frames=SEQUENCE_LENGTH,
                    draw_landmarks=True
                )
                
                # Emit frames for display
                for frame in frames:
                    self.frame_ready.emit(frame)
                
                # Save sequence with preview image (middle frame)
                preview_image = None
                if frames and len(frames) > 0:
                    preview_image = frames[len(frames) // 2]
                
                if not self.dataset_manager.save_captured_sequence(self.label, keypoints_list, preview_image):
                    self.finished.emit(False, f"Failed to save sequence {seq_idx}")
                    return
                
                # Update progress
                self.progress.emit(seq_idx + 1, self.num_sequences)
            
            self.finished.emit(True, f"Successfully captured {self.num_sequences} sequences")
            
        except Exception as e:
            app_logger.error(f"Capture error: {e}")
            self.finished.emit(False, str(e))
    
    def stop(self):
        """Stop capture."""
        self.is_running = False


class DatasetTab(QWidget):
    """Dataset creator tab for capturing training data."""
    
    def __init__(self):
        super().__init__()
        self.capture = ImageCapture()
        self.dataset_manager = DatasetManager()
        self.capture_worker = None
        self.is_capturing = False
        self.init_ui()
        
        # Timer for live preview
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dataset Creator")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # Camera preview
        preview_group = QGroupBox("Camera Preview")
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
        self.start_camera_btn = QPushButton("Start Camera")
        self.start_camera_btn.clicked.connect(self.toggle_camera)
        self.start_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        camera_controls.addWidget(self.start_camera_btn)
        preview_layout.addLayout(camera_controls)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Capture settings
        settings_group = QGroupBox("Capture Settings")
        settings_layout = QVBoxLayout()
        
        # Label name
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Gesture Label:"))
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Enter gesture name (e.g., 'Hello', 'Thanks')")
        label_layout.addWidget(self.label_input)
        settings_layout.addLayout(label_layout)
        
        # Number of sequences
        seq_layout = QHBoxLayout()
        seq_layout.addWidget(QLabel("Number of Sequences:"))
        self.seq_spinbox = QSpinBox()
        self.seq_spinbox.setMinimum(1)
        self.seq_spinbox.setMaximum(100)
        self.seq_spinbox.setValue(DEFAULT_CAPTURE_COUNT)
        seq_layout.addWidget(self.seq_spinbox)
        seq_layout.addStretch()
        settings_layout.addLayout(seq_layout)
        
        # Info label
        info_label = QLabel(f"Each sequence captures {SEQUENCE_LENGTH} frames (~1 second)")
        info_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        settings_layout.addWidget(info_label)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Progress
        progress_group = QGroupBox("Capture Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to capture")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Capture button
        self.capture_btn = QPushButton("Start Capture")
        self.capture_btn.clicked.connect(self.start_capture)
        self.capture_btn.setEnabled(False)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        layout.addWidget(self.capture_btn)
        
        # Dataset stats
        stats_group = QGroupBox("Dataset Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel()
        self.update_stats()
        stats_layout.addWidget(self.stats_label)
        
        refresh_btn = QPushButton("Refresh Stats")
        refresh_btn.clicked.connect(self.update_stats)
        stats_layout.addWidget(refresh_btn)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def toggle_camera(self):
        """Toggle camera on/off."""
        if not self.capture.is_capturing():
            if self.capture.start_capture():
                self.preview_timer.start(30)  # 30ms = ~33 FPS
                self.start_camera_btn.setText("Stop Camera")
                self.start_camera_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        padding: 10px;
                        font-size: 14px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                self.capture_btn.setEnabled(True)
            else:
                QMessageBox.critical(self, "Error", "Failed to start camera")
        else:
            self.preview_timer.stop()
            self.capture.stop_capture()
            self.start_camera_btn.setText("Start Camera")
            self.start_camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.capture_btn.setEnabled(False)
            self.preview_label.setText("Camera stopped")
    
    def update_preview(self):
        """Update camera preview."""
        ret, frame = self.capture.read_frame()
        if ret:
            # Process frame
            processed_frame, results = self.capture.process_frame(frame)
            processed_frame = self.capture.draw_landmarks(processed_frame, results)
            
            # Convert to QImage
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
    
    def start_capture(self):
        """Start capturing sequences."""
        label = self.label_input.text().strip()
        if not label:
            QMessageBox.warning(self, "Warning", "Please enter a gesture label")
            return
        
        if not self.capture.is_capturing():
            QMessageBox.warning(self, "Warning", "Please start the camera first")
            return
        
        num_sequences = self.seq_spinbox.value()
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Capture",
            f"Capture {num_sequences} sequences for gesture '{label}'?\n"
            f"Each sequence will be {SEQUENCE_LENGTH} frames.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Create label directory if needed
        self.dataset_manager.add_label(label)
        
        # Disable controls
        self.capture_btn.setEnabled(False)
        self.label_input.setEnabled(False)
        self.seq_spinbox.setEnabled(False)
        self.start_camera_btn.setEnabled(False)
        
        # Stop preview timer
        self.preview_timer.stop()
        
        # Start capture worker
        self.capture_worker = CaptureWorker(self.capture, label, num_sequences)
        self.capture_worker.progress.connect(self.on_capture_progress)
        self.capture_worker.frame_ready.connect(self.display_frame)
        self.capture_worker.finished.connect(self.on_capture_finished)
        self.capture_worker.start()
        
        self.progress_bar.setMaximum(num_sequences)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Capturing sequences for '{label}'...")
    
    def on_capture_progress(self, current, total):
        """Update capture progress."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Captured {current}/{total} sequences")
    
    def on_capture_finished(self, success, message):
        """Handle capture completion."""
        # Re-enable controls
        self.capture_btn.setEnabled(True)
        self.label_input.setEnabled(True)
        self.seq_spinbox.setEnabled(True)
        self.start_camera_btn.setEnabled(True)
        
        # Restart preview
        if self.capture.is_capturing():
            self.preview_timer.start(30)
        
        # Show result
        if success:
            QMessageBox.information(self, "Success", message)
            self.progress_label.setText("Capture completed successfully")
            self.update_stats()
        else:
            QMessageBox.critical(self, "Error", f"Capture failed: {message}")
            self.progress_label.setText("Capture failed")
        
        self.progress_bar.setValue(0)
    
    def update_stats(self):
        """Update dataset statistics."""
        stats = self.dataset_manager.get_stats()
        stats_text = f"<b>Total Labels:</b> {stats['total_labels']}<br>"
        stats_text += f"<b>Total Sequences:</b> {stats['total_sequences']}<br><br>"
        
        if stats['labels']:
            stats_text += "<b>Labels:</b><br>"
            for label, count in sorted(stats['labels'].items()):
                stats_text += f"  • {label}: {count} sequences<br>"
        else:
            stats_text += "<i>No data captured yet</i>"
        
        self.stats_label.setText(stats_text)
    
    def cleanup(self):
        """Cleanup resources."""
        if self.capture_worker and self.capture_worker.isRunning():
            self.capture_worker.stop()
            self.capture_worker.wait()
        
        self.preview_timer.stop()
        self.capture.stop_capture()
