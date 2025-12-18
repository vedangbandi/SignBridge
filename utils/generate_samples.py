import os
import cv2
import numpy as np
import sys
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import DATASET_DIR

LABELS = ["Hello", "Thanks", "Yes", "No", "Please", "Help", "Good_Bye", "I_Love_You"]
SAMPLE_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_hand.png")

def generate():
    print("Generating sample data (20 sequences per class)...")
    
    # Check if sample image exists
    sample_img = None
    if os.path.exists(SAMPLE_IMAGE_PATH):
        print(f"Using sample image: {SAMPLE_IMAGE_PATH}")
        sample_img = cv2.imread(SAMPLE_IMAGE_PATH)
        if sample_img is not None:
             # Resize to thumbnail size
            sample_img = cv2.resize(sample_img, (320, 240))
    else:
        print("Warning: Sample image not found, generating text placeholder.")

    for label in LABELS:
        label_path = os.path.join(DATASET_DIR, label)
        os.makedirs(label_path, exist_ok=True)
        
        # Create 20 sequences (Index 0 to 19)
        for seq_idx in range(20):
            seq_path = os.path.join(label_path, str(seq_idx))
            os.makedirs(seq_path, exist_ok=True)
            
            # 1. Save Preview Image
            target_img_path = os.path.join(seq_path, "preview.jpg")
            
            if sample_img is not None:
                cv2.imwrite(target_img_path, sample_img)
            else:
                # Fallback text image
                img = np.zeros((240, 320, 3), dtype=np.uint8)
                img[:] = (30, 30, 30)
                cv2.putText(img, label, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imwrite(target_img_path, img)
            
            # 2. Save Dummy Keypoints (30 frames)
            for i in range(30):
                # Create dummy keypoints (63 zeros)
                data = np.zeros(63) 
                np.save(os.path.join(seq_path, f"{i}.npy"), data)
            
        print(f"Created 20 samples for: {label}")

    print("Done! Dataset populated.")

if __name__ == "__main__":
    generate()
