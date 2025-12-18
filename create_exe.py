import os
import subprocess
import sys

def build():
    print("Building SignBridge Executable...")
    
    # 1. Install PyInstaller if not present (already checked)
    
    # 2. Define the command
    # --noconfirm: Overwrite output directory without asking
    # --windowed: No console window
    # --collect-all mediapipe: Crucial for MediaPipe assets
    # --name: Name of the exe
    # main.py: Entry point
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir", # Using onedir first for speed and size management
        "--windowed",
        "--name", "SignBridge",
        "--collect-all", "mediapipe",
        "--add-data", "ui;ui",
        "--add-data", "core;core",
        "--add-data", "utils;utils",
        "main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild Successful!")
        print(f"Executable can be found in: {os.path.join(os.getcwd(), 'dist', 'SignBridge')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
