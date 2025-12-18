"""
Main Window - Aurora UI (Glassmorphism Top Nav)
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolButton, QStackedWidget, QLabel, QFrame, 
    QScrollArea, QMessageBox, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QLinearGradient, QBrush, QPalette

from ui.dataset_tab import DatasetTab
from ui.browser_tab import BrowserTab
from ui.train_tab import TrainTab
from ui.predict_tab import PredictTab
from utils.config import WINDOW_TITLE
from utils.logger import app_logger

class MainWindow(QMainWindow):
    """Main App Window with Aurora UI."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        app_logger.info("Application started (Aurora UI)")
    
    def init_ui(self):
        self.setWindowTitle("SignBridge")
        self.resize(1200, 800)
        
        # --- Main Container ---
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Top Navigation Bar ---
        self.navbar = QFrame()
        self.navbar.setObjectName("NavBar")
        self.navbar.setFixedHeight(80)
        self.nav_layout = QHBoxLayout(self.navbar)
        self.nav_layout.setContentsMargins(20, 0, 20, 0)
        self.nav_layout.setSpacing(15)
        
        # Logo/Title
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 15, 0, 15)
        
        self.app_title = QLabel("SIGNBRIDGE")
        self.app_title.setObjectName("NavTitle")
        title_layout.addWidget(self.app_title)
        
        self.app_subtitle = QLabel("Gesture Intelligence")
        self.app_subtitle.setObjectName("NavSubtitle")
        title_layout.addWidget(self.app_subtitle)
        
        self.nav_layout.addWidget(title_container)
        self.nav_layout.addStretch()
        
        # Navigation Buttons
        self.buttons = []
        self.nav_layout.addWidget(self.create_nav_btn("Dataset Creator", 0))
        self.nav_layout.addWidget(self.create_nav_btn("Data Browser", 1))
        self.nav_layout.addWidget(self.create_nav_btn("Model Training", 2))
        self.nav_layout.addWidget(self.create_nav_btn("Live Prediction", 3))
        
        self.main_layout.addWidget(self.navbar)
        
        # --- Content Area (Scrollable) ---
        # We wrap the stacked widget in a ScrollArea to fix the "can't see bottom" issue
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setObjectName("ContentScroll")
        
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentStacked")
        
        # Initialize Tabs
        self.dataset_tab = DatasetTab()
        self.browser_tab = BrowserTab()
        self.train_tab = TrainTab()
        self.predict_tab = PredictTab()
        
        self.content_area.addWidget(self.dataset_tab)
        self.content_area.addWidget(self.browser_tab)
        self.content_area.addWidget(self.train_tab)
        self.content_area.addWidget(self.predict_tab)
        
        self.scroll_area.setWidget(self.content_area)
        self.main_layout.addWidget(self.scroll_area)
        
        # --- Stylesheet ---
        self.apply_stylesheet()
        
        # Set initial tab
        self.switch_tab(0)

    def create_nav_btn(self, text, index):
        btn = QToolButton()
        btn.setText(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(140, 40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_tab(index))
        self.buttons.append(btn)
        return btn
        
    def switch_tab(self, index):
        self.content_area.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* Backgrounds */
            QWidget#CentralWidget {
                background-color: #F3F4F6; /* Light Grey Background */
            }
            
            /* Navbar (Aurora Gradient) */
            QFrame#NavBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4c1d95, stop:1 #2563eb); /* Violet to Blue */
                border-bottom: 4px solid #1e40af;
            }
            
            QLabel#NavTitle {
                color: white;
                font-weight: 900;
                font-size: 22px;
                letter-spacing: 2px;
            }
            QLabel#NavSubtitle {
                color: #bfdbfe;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            /* Nav Buttons */
            QToolButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #e0e7ff;
                border: none;
                border-radius: 20px; /* Pill shape */
                font-weight: 600;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                color: white;
            }
            QToolButton:checked {
                background-color: white;
                color: #4c1d95; /* Text becomes purple */
                font-weight: 800;
            }
            
            /* Content Area */
            QScrollArea#ContentScroll {
                background-color: transparent;
            }
            QWidget#ContentStacked {
                background-color: transparent;
            }
            
            /* Tab Content Styling Override */
            /* Ensure tabs have a card-like appearance */
            
            /* Buttons inside tabs */
            QPushButton {
                background-color: #4c1d95;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5b21b6;
            }
            
            /* Inputs */
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                color: #1f2937;
            }
            
            /* Group Boxes */
            QGroupBox {
                background-color: white;
                border-radius: 12px;
                margin-top: 30px;
                border: 1px solid #e5e7eb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #4c1d95;
                font-weight: 800;
                font-size: 14px;
                background-color: transparent;
            }
            
            /* Lists */
            QListWidget {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #ede9fe; /* Light Purple */
                color: #4c1d95;
                border-left: 4px solid #4c1d95;
            }
        """)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Confirm Exit', 'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            app_logger.info("Application closing...")
            if hasattr(self.dataset_tab, 'cleanup'): self.dataset_tab.cleanup()
            if hasattr(self.predict_tab, 'cleanup'): self.predict_tab.cleanup()
            event.accept()
        else:
            event.ignore()
