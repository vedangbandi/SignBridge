"""
Dataset Browser Tab - GUI for browsing and managing dataset
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QGroupBox, QMessageBox, QInputDialog, QListWidgetItem,
    QSplitter, QFrame, QScrollArea, QSlider, QSizePolicy, QFileDialog,
    QProgressDialog
)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QIcon
import os
import cv2
import numpy as np
from core.label_manager import LabelManager
from core.image_capture import ImageCapture
from utils.file_ops import get_sequence_count, delete_sequence, get_label_path, load_sequence, save_sequence
import utils.config as config
from utils.logger import app_logger


class HandVisualizer(QLabel):
    """Widget to visualize hand landmarks or preview images."""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(100, 100)  # Allow shrinking
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #2C3E50; border: 2px solid #34495E; border-radius: 8px;")
        self.setAlignment(Qt.AlignCenter)
        self.keypoints = None
        self.clear_visual()
        
    def clear_visual(self):
        self.setText("Select a sequence to preview")
        self.keypoints = None
        self.update()
        
    def set_keypoints(self, keypoints):
        """Draw keypoints on the widget."""
        self.keypoints = keypoints
        self.setText("")
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Keypoints if available
        if self.keypoints is None:
            return
            
        if len(self.keypoints) != config.KEYPOINTS_PER_FRAME:
            return
            
        # Draw text if viewing keypoints
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, 20, "Keypoint Visualization (No Image)")

        points = []
        for i in range(0, 63, 3):
            points.append((self.keypoints[i], self.keypoints[i+1]))
            
        # Calculate scale to fit keypoints in widget maintaining 4:3 aspect ratio
        # Standard webcam is 4:3
        target_ratio = 4.0 / 3.0
        widget_ratio = self.width() / self.height()
        
        padding = 20
        available_w = self.width() - 2 * padding
        available_h = self.height() - 2 * padding
        
        if available_w / available_h > target_ratio:
            # Widget is wider than target
            draw_h = available_h
            draw_w = int(draw_h * target_ratio)
            offset_x = padding + (available_w - draw_w) // 2
            offset_y = padding
        else:
            # Widget is taller than target
            draw_w = available_w
            draw_h = int(draw_w / target_ratio)
            offset_x = padding
            offset_y = padding + (available_h - draw_h) // 2
        
        # Map normalized points to widget size
        mapped_points = []
        for x, y in points:
            if x == 0 and y == 0: continue
            px = int(x * draw_w) + offset_x
            py = int(y * draw_h) + offset_y
            mapped_points.append((px, py))
            
        if not mapped_points:
            return

        # Draw connections
        painter.setPen(QPen(QColor("#2ECC71"), 2))
        
        def get_pt(idx):
            if idx*3+1 >= len(self.keypoints): return None
            x = self.keypoints[idx*3]
            y = self.keypoints[idx*3+1]
            if x==0 and y==0: return None
            return int(x * draw_w) + offset_x, int(y * draw_h) + offset_y

        if config.HAND_CONNECTIONS:
            for start, end in config.HAND_CONNECTIONS:
                p1 = get_pt(start)
                p2 = get_pt(end)
                if p1 and p2:
                    painter.drawLine(p1[0], p1[1], p2[0], p2[1])

        # Draw points
        painter.setPen(QPen(QColor("#E74C3C"), 5))
        for px, py in mapped_points:
            painter.drawPoint(px, py)


class RepairDatasetWorker(QThread):
    """Worker thread to generate missing keypoint data from images in the dataset."""
    progress = pyqtSignal(int, int, str) # current, total, label
    finished = pyqtSignal(int, int) # added, total_checked

    def __init__(self, dataset_path):
        super().__init__()
        self.dataset_path = dataset_path
        self.processor = ImageCapture()
        # Initialize hands without starting camera
        import mediapipe as mp
        self.processor.hands = mp.solutions.hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )

    def run(self):
        added_count = 0
        total_checked = 0
        
        labels = [d for d in os.listdir(self.dataset_path) 
                  if os.path.isdir(os.path.join(self.dataset_path, d))]
        
        # 1. AUTO-IMPORT: Find loose images in label folders
        self.progress.emit(0, 100, "Scanning for loose images...")
        for label in labels:
            label_dir = os.path.join(self.dataset_path, label)
            loose_images = [f for f in os.listdir(label_dir) 
                           if f.lower().endswith(('.jpg', '.png', '.jpeg')) 
                           and os.path.isfile(os.path.join(label_dir, f))]
            
            if loose_images:
                # Calculate next sequence index
                existing_dirs = [d for d in os.listdir(label_dir) if os.path.isdir(os.path.join(label_dir, d))]
                indices = []
                for d in existing_dirs:
                    try: indices.append(int(d))
                    except: pass
                next_idx = max(indices) + 1 if indices else 0
                
                for img_name in loose_images:
                    self.progress.emit(0, 0, f"Importing {label}/{img_name}...")
                    old_path = os.path.join(label_dir, img_name)
                    
                    # Read and process
                    frame = cv2.imread(old_path)
                    if frame is not None:
                        # Extract landmarks
                        results = self.processor.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        kp = self.processor.extract_keypoints(results)
                        
                        # Save sequence
                        save_sequence(label, next_idx, [kp for _ in range(config.SEQUENCE_LENGTH)])
                        
                        # Move image to its new home (sequence_dir/preview.jpg)
                        # This auto-cleans the label folder
                        new_seq_dir = os.path.join(label_dir, str(next_idx))
                        os.makedirs(new_seq_dir, exist_ok=True)
                        
                        # Rename/move file instead of copying to keep it clean
                        target_img_path = os.path.join(new_seq_dir, "preview.jpg")
                        try:
                            # Re-save as preview.jpg to ensure consistency
                            cv2.imwrite(target_img_path, frame)
                            os.remove(old_path)
                            added_count += 1
                            next_idx += 1
                        except: pass

        # 2. REPAIR: Check existing sequences for missing landmarks
        all_sequences = []
        for label in labels:
            label_dir = os.path.join(self.dataset_path, label)
            seqs = [d for d in os.listdir(label_dir) if os.path.isdir(os.path.join(label_dir, d))]
            for s in seqs:
                all_sequences.append((label, s))
        
        total_total = len(all_sequences)
        
        for i, (label, seq_idx) in enumerate(all_sequences):
            seq_path = os.path.join(self.dataset_path, label, seq_idx)
            kp_path = os.path.join(seq_path, "keypoints.npy")
            
            self.progress.emit(i + 1, total_total, f"Repairing {label}/{seq_idx}...")
            total_checked += 1
            
            if not os.path.exists(kp_path):
                # Try to find images to process
                img_path = os.path.join(seq_path, "preview.jpg")
                if not os.path.exists(img_path):
                    imgs = [f for f in os.listdir(seq_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                    if imgs: img_path = os.path.join(seq_path, imgs[0])
                
                if os.path.exists(img_path):
                    frame = cv2.imread(img_path)
                    if frame is not None:
                        results = self.processor.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        kp = self.processor.extract_keypoints(results)
                        save_sequence(label, int(seq_idx), [kp for _ in range(config.SEQUENCE_LENGTH)])
                        added_count += 1
        
        self.finished.emit(added_count, total_checked)
        self.processor.stop_capture()


class BrowserTab(QWidget):
    """Dataset browser tab for managing labels and sequences."""
    
    def __init__(self):
        super().__init__()
        self.label_manager = LabelManager()
        self.current_label = None
        self.current_sequence_frames = []
        self.current_frame_idx = 0
        self.is_playing = False
        self.init_ui()
        self.refresh_labels()
        
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_frame)
    
    def init_ui(self):
        """Initialize UI components."""
        # Top-level vertical layout
        top_layout = QVBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(10, 10, 10, 10)

        # --- Dataset Selector Bar ---
        selector_bar = QHBoxLayout()
        self.dataset_path_label = QLabel(f"<b>Current Dataset:</b> {config.DATASET_PATH}")
        self.dataset_path_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        
        self.sync_btn = QPushButton("🔄 Sync & Repair")
        self.sync_btn.setFixedSize(130, 30)
        self.sync_btn.setToolTip("Generate missing .npy data from images in the dataset folder")
        self.sync_btn.setStyleSheet("background-color: #27AE60; color: white; border-radius: 4px;")
        self.sync_btn.clicked.connect(self.repair_dataset)

        self.browse_btn = QPushButton("📂 Browse Dataset")
        self.browse_btn.setFixedSize(150, 30)
        self.browse_btn.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; border-radius: 4px;")
        self.browse_btn.clicked.connect(self.browse_dataset)
        
        selector_bar.addWidget(self.dataset_path_label)
        selector_bar.addStretch()
        selector_bar.addWidget(self.sync_btn)
        selector_bar.addWidget(self.browse_btn)
        top_layout.addLayout(selector_bar)

        # Main Horizontal Layout for 3 Columns
        main_layout = QHBoxLayout()
        main_layout.setSpacing(2) # Near zero spacing between columns
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Column 1: Labels ---
        col1 = QGroupBox("1. Select Class")
        col1.setMaximumWidth(250) # Fix width to prevent gaps
        col1_layout = QVBoxLayout()
        
        self.label_list = QListWidget()
        self.label_list.setMinimumHeight(200) # Ensure it has some base size
        self.label_list.itemClicked.connect(self.on_label_selected)
        col1_layout.addWidget(self.label_list)

        
        # Label Controls
        label_controls = QHBoxLayout()
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_label)
        self.delete_label_btn = QPushButton("Delete")
        self.delete_label_btn.clicked.connect(self.delete_label)
        self.delete_label_btn.setStyleSheet("background-color: #E74C3C; color: white;")
        label_controls.addWidget(self.rename_btn)
        label_controls.addWidget(self.delete_label_btn)
        col1_layout.addLayout(label_controls)
        col1_layout.addStretch() # Push everything to the top
        
        col1.setLayout(col1_layout)
        main_layout.addWidget(col1, 0) # No stretch
        
        # --- Column 2: Sequences ---
        
        # Column 2: Sequences (Narrow)
        col2 = QGroupBox("2. Sequence")
        col2.setMaximumWidth(250) # Fix width to prevent gaps
        col2_layout = QVBoxLayout()
        self.sequence_list = QListWidget()
        self.sequence_list.setMinimumHeight(200) # Ensure it has some base size
        self.sequence_list.setSelectionMode(QListWidget.SingleSelection)
        self.sequence_list.setIconSize(QSize(32, 32))  # Smaller icons for list
        self.sequence_list.itemClicked.connect(self.on_sequence_selected)
        col2_layout.addWidget(self.sequence_list)

        # Sequence Controls
        seq_controls = QHBoxLayout()
        self.delete_seq_btn = QPushButton("Delete Sequence")
        self.delete_seq_btn.clicked.connect(self.delete_sequence)
        self.delete_seq_btn.setStyleSheet("background-color: #E74C3C; color: white;")
        seq_controls.addWidget(self.delete_seq_btn)
        col2_layout.addLayout(seq_controls)
        col2_layout.addStretch() # Push everything to the top

        col2.setLayout(col2_layout)
        main_layout.addWidget(col2, 0) # No stretch
        
        # Column 3: Preview (Wide)
        col3 = QGroupBox("3. Visualization")
        col3_layout = QVBoxLayout()
        col3_layout.setSpacing(2) # Minimal spacing
        col3_layout.setAlignment(Qt.AlignTop)
        
        # -- Controls (Moved to Top) --
        controls_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(40, 30)
        self.prev_btn.clicked.connect(self.prev_frame)
        controls_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(40, 30)
        self.next_btn.clicked.connect(self.next_frame)
        controls_layout.addWidget(self.next_btn)
        
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)
        controls_layout.addWidget(self.frame_slider)
        
        self.frame_label = QLabel("Frame: 0/0")
        controls_layout.addWidget(self.frame_label)
        
        col3_layout.addLayout(controls_layout)
        
        # -- Visualizer (Keypoints) --
        col3_layout.addSpacing(10)
        col3_layout.addWidget(QLabel("Keypoint Skeleton:"), 0, Qt.AlignCenter)
        self.visualizer = HandVisualizer()
        self.visualizer.setFixedSize(400, 300) # Identical Normalized Size
        col3_layout.addWidget(self.visualizer, 0, Qt.AlignCenter)
        
        # -- Actual Image (Moved to Bottom) --
        col3_layout.addSpacing(20)
        col3_layout.addWidget(QLabel("Reference Image:"), 0, Qt.AlignCenter)
        self.image_label = QLabel("Select a sequence")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000; border: 1px solid #555; border-radius: 4px;")
        self.image_label.setFixedSize(400, 300) # Identical Normalized Size
        col3_layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        
        col3.setLayout(col3_layout)
        
        # Add columns with new ratios
        # col1 and col2 added above
        main_layout.addWidget(col3, 1) # Takes remaining space
        top_layout.addLayout(main_layout)
        
        self.setLayout(top_layout)

    def browse_dataset(self):
        """Open dialog to browse for a new dataset directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Dataset Directory", config.DATASET_PATH
        )
        
        if dir_path:
            config.update_dataset_path(dir_path)
            self.dataset_path_label.setText(f"<b>Current Dataset:</b> {dir_path}")
            app_logger.info(f"Updated dataset path to: {dir_path}")
            
            # Refresh everything
            self.label_manager.refresh()
            self.refresh_labels()
            self.current_label = None
            self.sequence_list.clear()
            self.visualizer.clear_visual()
            self.image_label.setText("Select a sequence")
            self.image_label.setPixmap(QPixmap())
            
            QMessageBox.information(self, "Dataset Updated", f"Loaded dataset from:\n{dir_path}")

    def repair_dataset(self):
        """Find images without .npy files and generate them."""
        self.progress_dialog = QProgressDialog("Scanning dataset...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setWindowTitle("Dataset Sync")
        self.progress_dialog.show()

        self.repair_worker = RepairDatasetWorker(config.DATASET_PATH)
        self.repair_worker.progress.connect(self.on_repair_progress)
        self.repair_worker.finished.connect(self.on_repair_finished)
        self.repair_worker.start()

    def on_repair_progress(self, current, total, text):
        self.progress_dialog.setMaximum(total)
        self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(f"Processing: {text}")
        if self.progress_dialog.wasCanceled():
            self.repair_worker.terminate()

    def on_repair_finished(self, added, checked):
        self.progress_dialog.close()
        self.refresh_labels()
        if added > 0:
            QMessageBox.information(self, "Sync Complete", 
                                    f"Successfully repaired the dataset!\n\n"
                                    f"• Generated landmarks for {added} sequences.\n"
                                    f"• Scanned {checked} total sequences.")
        else:
            QMessageBox.information(self, "Sync Complete", 
                                    f"Dataset is already in sync!\n\n"
                                    f"All {checked} sequences have valid landmark data.")


    def refresh_labels(self):
        """Refresh labels list."""
        self.label_list.clear()
        self.label_manager.refresh()
        labels = self.label_manager.get_all_labels()
        for label in labels:
            seq_count = get_sequence_count(label)
            item = QListWidgetItem(f"{label} ({seq_count})")
            item.setData(Qt.UserRole, label)
            self.label_list.addItem(item)
            
        self.sequence_list.clear()
        self.visualizer.clear_visual()
        self.image_label.setText("Select a sequence")
        self.image_label.setPixmap(QPixmap()) # Clear any previous image



    def on_label_selected(self, item):
        """Handle label selection."""
        self.current_label = item.data(Qt.UserRole)
        self.refresh_sequences()
        self.visualizer.clear_visual()
        self.image_label.setText("Select a sequence")
        self.image_label.setPixmap(QPixmap()) # Clear any previous image
        self.current_sequence_frames = []


    def on_sequence_selected(self, item):
        """Load sequence data when selected."""
        seq_idx = item.data(Qt.UserRole)
        self.load_sequence(seq_idx)

    def refresh_sequences(self):
        """Refresh sequences list for current label."""
        self.sequence_list.clear()
        if not self.current_label: return
        
        label_path = get_label_path(self.current_label)
        seq_count = get_sequence_count(self.current_label)
        
        for i in range(seq_count):
            item = QListWidgetItem(f"Sequence {i}")
            item.setData(Qt.UserRole, i)
            
            # Check for preview image
            seq_path = os.path.join(label_path, str(i))
            img_path = os.path.join(seq_path, "preview.jpg")
            
            if os.path.exists(img_path):
                icon = QIcon(img_path)
                item.setIcon(icon)
                
            self.sequence_list.addItem(item)

    def load_sequence(self, seq_idx):
        """Load sequence data."""
        if not self.current_label: return
        
        label_path = get_label_path(self.current_label)
        sequence_path = os.path.join(label_path, str(seq_idx))
        if not os.path.exists(sequence_path): return

        # 1. Load Image
        preview_img_path = os.path.join(sequence_path, "preview.jpg")
        if os.path.exists(preview_img_path):
            pixmap = QPixmap(preview_img_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self.image_label.setText("Error loading image")
        else:
            # Debug info
            short_path = "..." + preview_img_path[-40:] if len(preview_img_path) > 40 else preview_img_path
            self.image_label.setText(f"No Image Found\n\nExpected at:\n{short_path}")
            self.image_label.setPixmap(QPixmap()) # Clear

        # 2. Load Keypoints
        frames = load_sequence(self.current_label, seq_idx, config.SEQUENCE_LENGTH)
            
        self.current_sequence_frames = frames if frames is not None else []
        self.current_frame_idx = 0
        
        if len(self.current_sequence_frames) > 0:
            self.update_visual()
            self.frame_slider.setMaximum(len(self.current_sequence_frames) - 1)
            self.frame_slider.setValue(0)
        else:
            self.visualizer.clear_visual()
            self.frame_slider.setMaximum(0)
            
        self.is_playing = False
        self.play_btn.setText("▶ Play")

    def update_visual(self):
        """Update the visualizer with current keypoint frame."""
        if self.current_sequence_frames is None or len(self.current_sequence_frames) == 0:
            return
            
        if 0 <= self.current_frame_idx < len(self.current_sequence_frames):
            data = self.current_sequence_frames[self.current_frame_idx]
            self.visualizer.set_keypoints(data)
            self.frame_label.setText(f"Frame: {self.current_frame_idx + 1}/{len(self.current_sequence_frames)}")

    def prev_frame(self):
        """Go to previous frame."""
        val = self.frame_slider.value()
        if val > 0:
            self.frame_slider.setValue(val - 1)
            
    def next_frame(self):
        """Go to next frame."""
        val = self.frame_slider.value()
        if val < self.frame_slider.maximum():
            self.frame_slider.setValue(val + 1)
            
    def on_slider_changed(self, value):
        """Handle slider value change."""
        self.current_frame_idx = value
        self.update_visual()

    def toggle_play(self):
        """Toggle animation playback."""
        if self.anim_timer.isActive(): # Changed from self.timer to self.anim_timer to match existing code
            self.anim_timer.stop()
            self.play_btn.setText("▶ Play")
        else:
            if self.current_sequence_frames is None or len(self.current_sequence_frames) == 0:
                return
            
            # Restart if at end
            if self.frame_slider.value() >= self.frame_slider.maximum():
                self.frame_slider.setValue(0)
                
            self.anim_timer.start(100) # Changed from self.timer.start() to self.anim_timer.start(100) to match existing code
            self.play_btn.setText("⏸ Pause")

    def rename_label(self):
        if not self.current_label: return
        new_label, ok = QInputDialog.getText(self, "Rename", "New Name:", text=self.current_label)
        if ok and new_label:
            if self.label_manager.rename(self.current_label, new_label):
                self.refresh_labels()

    def delete_label(self):
        if not self.current_label: return
        self.label_manager.delete(self.current_label)
        self.refresh_labels()

    def delete_sequence(self):
        item = self.sequence_list.currentItem()
        if not item: return
        seq_idx = item.data(Qt.UserRole)
        delete_sequence(self.current_label, seq_idx)
        self.refresh_sequences()
        self.visualizer.clear_visual()
