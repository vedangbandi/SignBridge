"""
Training Tab - GUI for model training
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox, QTextEdit, QProgressBar,
    QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from core.dataset_manager import DatasetManager
from core.trainer import Trainer
from utils.config import (
    DEFAULT_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
    DEFAULT_VALIDATION_SPLIT
)
from utils.logger import training_logger
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class TrainingPlot(FigureCanvasQTAgg):
    """Real-time training plot."""
    
    def __init__(self, parent=None):
        fig = Figure(figsize=(8, 4))
        self.axes_loss = fig.add_subplot(121)
        self.axes_acc = fig.add_subplot(122)
        super().__init__(fig)
        
        self.train_loss = []
        self.val_loss = []
        self.train_acc = []
        self.val_acc = []
        
        self.setup_plots()
    
    def setup_plots(self):
        """Setup plot axes."""
        self.axes_loss.set_title('Loss')
        self.axes_loss.set_xlabel('Epoch')
        self.axes_loss.set_ylabel('Loss')
        self.axes_loss.grid(True, alpha=0.3)
        
        self.axes_acc.set_title('Accuracy')
        self.axes_acc.set_xlabel('Epoch')
        self.axes_acc.set_ylabel('Accuracy')
        self.axes_acc.grid(True, alpha=0.3)
    
    def update_plot(self, epoch, logs):
        """Update plots with new data."""
        self.train_loss.append(logs.get('loss', 0))
        self.val_loss.append(logs.get('val_loss', 0))
        self.train_acc.append(logs.get('categorical_accuracy', 0))
        self.val_acc.append(logs.get('val_categorical_accuracy', 0))
        
        epochs = list(range(1, len(self.train_loss) + 1))
        
        # Update loss plot
        self.axes_loss.clear()
        self.axes_loss.plot(epochs, self.train_loss, 'b-', label='Training Loss')
        self.axes_loss.plot(epochs, self.val_loss, 'r-', label='Validation Loss')
        self.axes_loss.set_title('Loss')
        self.axes_loss.set_xlabel('Epoch')
        self.axes_loss.set_ylabel('Loss')
        self.axes_loss.legend()
        self.axes_loss.grid(True, alpha=0.3)
        
        # Update accuracy plot
        self.axes_acc.clear()
        self.axes_acc.plot(epochs, self.train_acc, 'b-', label='Training Accuracy')
        self.axes_acc.plot(epochs, self.val_acc, 'r-', label='Validation Accuracy')
        self.axes_acc.set_title('Accuracy')
        self.axes_acc.set_xlabel('Epoch')
        self.axes_acc.set_ylabel('Accuracy')
        self.axes_acc.legend()
        self.axes_acc.grid(True, alpha=0.3)
        
        self.draw()
    
    def reset(self):
        """Reset plots."""
        self.train_loss = []
        self.val_loss = []
        self.train_acc = []
        self.val_acc = []
        self.axes_loss.clear()
        self.axes_acc.clear()
        self.setup_plots()
        self.draw()


class TrainingWorker(QThread):
    """Worker thread for model training."""
    
    progress = pyqtSignal(int, dict)  # epoch, logs
    log_message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, dataset_manager, epochs, batch_size, learning_rate, val_split):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.val_split = val_split
        self.trainer = Trainer()
    
    def run(self):
        """Run training."""
        try:
            self.log_message.emit("Loading dataset...")
            
            # Load data
            X, y, labels = self.dataset_manager.load_all_data()
            if X is None or y is None:
                self.finished.emit(False, "Failed to load dataset")
                return
            
            self.log_message.emit(f"Loaded {len(X)} samples with {len(labels)} labels")
            self.log_message.emit(f"Labels: {', '.join(labels)}")
            
            # Prepare data
            self.log_message.emit("Preparing data...")
            X_train, X_val, y_train, y_val = self.trainer.prepare_data(
                X, y, labels, self.val_split
            )
            
            self.log_message.emit(f"Training samples: {len(X_train)}")
            self.log_message.emit(f"Validation samples: {len(X_val)}")
            
            # Train model
            self.log_message.emit("Starting training...")
            success = self.trainer.train(
                X_train, y_train, X_val, y_val,
                epochs=self.epochs,
                batch_size=self.batch_size,
                learning_rate=self.learning_rate,
                progress_callback=self.on_epoch_end
            )
            
            if success:
                # Save model
                self.log_message.emit("Saving model...")
                if self.trainer.save_model():
                    self.finished.emit(True, "Training completed successfully!")
                else:
                    self.finished.emit(False, "Training completed but failed to save model")
            else:
                self.finished.emit(False, "Training failed")
                
        except Exception as e:
            training_logger.error(f"Training error: {e}")
            self.finished.emit(False, str(e))
    
    def on_epoch_end(self, epoch, logs):
        """Callback for epoch end."""
        self.progress.emit(epoch + 1, logs)
        
        log_msg = f"Epoch {epoch + 1}/{self.epochs} - "
        log_msg += f"loss: {logs.get('loss', 0):.4f} - "
        log_msg += f"acc: {logs.get('categorical_accuracy', 0):.4f} - "
        log_msg += f"val_loss: {logs.get('val_loss', 0):.4f} - "
        log_msg += f"val_acc: {logs.get('val_categorical_accuracy', 0):.4f}"
        
        self.log_message.emit(log_msg)


class TrainTab(QWidget):
    """Training tab for model training."""
    
    def __init__(self):
        super().__init__()
        self.dataset_manager = DatasetManager()
        self.training_worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        # Main layout with reduced spacing
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Model Training")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # --- Training Parameters (Grid Layout) ---
        params_group = QGroupBox("Training Parameters")
        params_layout = QGridLayout()
        params_layout.setVerticalSpacing(5)
        params_layout.setHorizontalSpacing(15)
        
        # Epochs
        params_layout.addWidget(QLabel("Epochs:"), 0, 0)
        self.epochs_spinbox = QSpinBox()
        self.epochs_spinbox.setMinimum(1)
        self.epochs_spinbox.setMaximum(500)
        self.epochs_spinbox.setValue(DEFAULT_EPOCHS)
        self.epochs_spinbox.setMinimumWidth(100)
        params_layout.addWidget(self.epochs_spinbox, 0, 1)
        
        # Batch Size
        params_layout.addWidget(QLabel("Batch Size:"), 0, 2)
        self.batch_spinbox = QSpinBox()
        self.batch_spinbox.setRange(1, 128)
        self.batch_spinbox.setValue(DEFAULT_BATCH_SIZE)
        self.batch_spinbox.setMinimumWidth(100)
        params_layout.addWidget(self.batch_spinbox, 0, 3)
        
        # Learning Rate (Wider for visibility)
        params_layout.addWidget(QLabel("Learning Rate:"), 1, 0)
        self.lr_spinbox = QDoubleSpinBox()
        self.lr_spinbox.setDecimals(5)
        self.lr_spinbox.setRange(0.00001, 1.0)
        self.lr_spinbox.setSingleStep(0.0001)
        self.lr_spinbox.setValue(DEFAULT_LEARNING_RATE)
        self.lr_spinbox.setMinimumWidth(120) 
        params_layout.addWidget(self.lr_spinbox, 1, 1)
        
        # Validation Split
        params_layout.addWidget(QLabel("Validation Split:"), 1, 2)
        self.val_spinbox = QDoubleSpinBox()
        self.val_spinbox.setDecimals(2)
        self.val_spinbox.setRange(0.1, 0.5)
        self.val_spinbox.setSingleStep(0.05)
        self.val_spinbox.setValue(DEFAULT_VALIDATION_SPLIT)
        self.val_spinbox.setMinimumWidth(100)
        params_layout.addWidget(self.val_spinbox, 1, 3)
        
        # Add stretch to keep it compact
        params_layout.setColumnStretch(4, 1)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # --- Controls ---
        controls_layout = QHBoxLayout()
        controls_layout.addStretch() # Center buttons
        self.validate_btn = QPushButton("Validate Dataset")
        self.validate_btn.clicked.connect(self.validate_dataset)
        self.validate_btn.setStyleSheet("background-color: #F39C12; color: white; padding: 6px; border-radius: 4px; min-width: 140px;")
        controls_layout.addWidget(self.validate_btn)
        
        self.train_btn = QPushButton("Start Training")
        self.train_btn.clicked.connect(self.start_training)
        self.train_btn.setStyleSheet("background-color: #27AE60; color: white; padding: 6px; font-weight: bold; border-radius: 4px; min-width: 140px;")
        controls_layout.addWidget(self.train_btn)
        controls_layout.addStretch() # Center buttons
        layout.addLayout(controls_layout)
        
        # --- Progress ---
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(2)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12) 
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ready to train")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)
        
        # --- Plot ---
        self.training_plot = TrainingPlot()
        self.training_plot.setFixedHeight(250) # Reduced fixed height
        layout.addWidget(self.training_plot)
        
        # --- Logs ---
        log_group = QGroupBox("Training Logs")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(5, 5, 5, 5)
        log_layout.setSpacing(0)
        log_layout.setAlignment(Qt.AlignTop)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'Consolas', 'Courier New'; font-size: 10pt; border: none;")
        self.log_text.setFixedHeight(80) # Fixed height for text
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        log_group.setFixedHeight(110) # Fixed group height (header + text + margins)
        layout.addWidget(log_group)
        
        layout.addStretch() # Push everything up to reduce blank space between boxes
        
        self.setLayout(layout)
    
    def validate_dataset(self):
        """Validate dataset for training."""
        self.dataset_manager.refresh_labels()
        is_valid, message = self.dataset_manager.validate_dataset()
        
        if is_valid:
            QMessageBox.information(self, "Dataset Valid", message)
        else:
            QMessageBox.warning(self, "Dataset Invalid", message)
    
    def start_training(self):
        """Start model training."""
        # Validate dataset first
        self.dataset_manager.refresh_labels()
        is_valid, message = self.dataset_manager.validate_dataset()
        
        if not is_valid:
            QMessageBox.warning(self, "Dataset Invalid", message)
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Training",
            f"Start training with:\n"
            f"  • Epochs: {self.epochs_spinbox.value()}\n"
            f"  • Batch Size: {self.batch_spinbox.value()}\n"
            f"  • Learning Rate: {self.lr_spinbox.value()}\n"
            f"  • Validation Split: {self.val_spinbox.value()}\n\n"
            f"This may take several minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Disable controls
        self.train_btn.setEnabled(False)
        self.validate_btn.setEnabled(False)
        self.epochs_spinbox.setEnabled(False)
        self.batch_spinbox.setEnabled(False)
        self.lr_spinbox.setEnabled(False)
        self.val_spinbox.setEnabled(False)
        
        # Reset plot and log
        self.training_plot.reset()
        self.log_text.clear()
        
        # Setup progress
        self.progress_bar.setMaximum(self.epochs_spinbox.value())
        self.progress_bar.setValue(0)
        
        # Start training worker
        self.training_worker = TrainingWorker(
            self.dataset_manager,
            self.epochs_spinbox.value(),
            self.batch_spinbox.value(),
            self.lr_spinbox.value(),
            self.val_spinbox.value()
        )
        self.training_worker.progress.connect(self.on_training_progress)
        self.training_worker.log_message.connect(self.on_log_message)
        self.training_worker.finished.connect(self.on_training_finished)
        self.training_worker.start()
        
        self.log_message("Training started...")
    
    def on_training_progress(self, epoch, logs):
        """Update training progress."""
        self.progress_bar.setValue(epoch)
        self.progress_label.setText(f"Epoch {epoch}/{self.epochs_spinbox.value()}")
        self.training_plot.update_plot(epoch, logs)
    
    def on_log_message(self, message):
        """Add message to log."""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def log_message(self, message):
        """Add message to log."""
        self.on_log_message(message)
    
    def on_training_finished(self, success, message):
        """Handle training completion."""
        # Re-enable controls
        self.train_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
        self.epochs_spinbox.setEnabled(True)
        self.batch_spinbox.setEnabled(True)
        self.lr_spinbox.setEnabled(True)
        self.val_spinbox.setEnabled(True)
        
        # Show result
        if success:
            QMessageBox.information(self, "Success", message)
            self.progress_label.setText("Training completed successfully")
            self.log_message("✓ " + message)
        else:
            QMessageBox.critical(self, "Error", f"Training failed: {message}")
            self.progress_label.setText("Training failed")
            self.log_message("✗ " + message)
