"""
SignBridge: Bridging Sign Language and Trainable Hand Gestures
Main Entry Point

A comprehensive application for creating datasets, training models,
and performing real-time sign language recognition.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from utils.logger import app_logger


def main():
    """Main application entry point."""
    try:
        # Enable high DPI scaling (must be set before QApplication)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("SignBridge")
        app.setOrganizationName("SLR Team")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        app_logger.info("Application window displayed")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        app_logger.error(f"Application error: {e}", exc_info=True)
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("SignBridge: Bridging Sign Language and Trainable Hand Gestures")
    print("=" * 60)
    print("\nStarting application...")
    print("Please wait while the GUI loads...\n")
    
    main()
