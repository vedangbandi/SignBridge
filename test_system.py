"""
Test script to verify the Sign Language Recognition System
This script checks:
1. Data integrity in MP_Data
2. Model training capability
3. Real-time prediction functionality
"""

import os
import numpy as np
from function import *

def test_data_integrity():
    """Test if MP_Data has all required files"""
    print("=" * 60)
    print("TESTING DATA INTEGRITY")
    print("=" * 60)
    
    missing_files = []
    total_files = 0
    
    for action in actions:
        action_path = os.path.join(DATA_PATH, action)
        if not os.path.exists(action_path):
            print(f"❌ Missing action directory: {action}")
            continue
            
        for sequence in range(no_sequences):
            sequence_path = os.path.join(action_path, str(sequence))
            if not os.path.exists(sequence_path):
                print(f"❌ Missing sequence directory: {action}/{sequence}")
                continue
                
            for frame_num in range(sequence_length):
                file_path = os.path.join(sequence_path, f"{frame_num}.npy")
                total_files += 1
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
    
    print(f"\nTotal expected files: {len(actions) * no_sequences * sequence_length}")
    print(f"Total files checked: {total_files}")
    print(f"Missing files: {len(missing_files)}")
    
    if len(missing_files) > 0:
        print(f"\n⚠️  Warning: {len(missing_files)} files are missing!")
        print("First 10 missing files:")
        for f in missing_files[:10]:
            print(f"  - {f}")
    else:
        print("\n✅ All data files are present!")
    
    return len(missing_files) == 0

def test_data_loading():
    """Test if data can be loaded correctly"""
    print("\n" + "=" * 60)
    print("TESTING DATA LOADING")
    print("=" * 60)
    
    try:
        # Try loading a few samples
        sample_action = actions[0]
        sample_sequence = 0
        
        print(f"\nLoading sample: {sample_action}/{sample_sequence}")
        
        window = []
        for frame_num in range(sequence_length):
            file_path = os.path.join(DATA_PATH, sample_action, str(sample_sequence), f"{frame_num}.npy")
            data = np.load(file_path, allow_pickle=True)
            window.append(data)
            
        window_array = np.array(window)
        print(f"✅ Successfully loaded sequence")
        print(f"   Shape: {window_array.shape}")
        print(f"   Expected shape: ({sequence_length}, 63)")
        
        if window_array.shape == (sequence_length, 63):
            print("✅ Data shape is correct!")
            return True
        else:
            print(f"❌ Data shape mismatch!")
            return False
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def test_extract_keypoints():
    """Test the extract_keypoints function"""
    print("\n" + "=" * 60)
    print("TESTING EXTRACT_KEYPOINTS FUNCTION")
    print("=" * 60)
    
    # Test with None results (no hand detected)
    class MockResults:
        multi_hand_landmarks = None
    
    results = MockResults()
    keypoints = extract_keypoints(results)
    
    if keypoints is not None and keypoints.shape == (63,):
        print("✅ extract_keypoints handles no hand detection correctly")
        print(f"   Returns zero array with shape: {keypoints.shape}")
        return True
    else:
        print("❌ extract_keypoints doesn't handle no hand detection properly")
        return False

def test_model_files():
    """Test if model files exist"""
    print("\n" + "=" * 60)
    print("TESTING MODEL FILES")
    print("=" * 60)
    
    model_json_exists = os.path.exists("model.json")
    model_h5_exists = os.path.exists("model.h5")
    
    print(f"model.json exists: {'✅' if model_json_exists else '❌'}")
    print(f"model.h5 exists: {'✅' if model_h5_exists else '❌'}")
    
    if model_json_exists and model_h5_exists:
        print("\n✅ Model files are present!")
        return True
    else:
        print("\n⚠️  Model files are missing. Run trainmodel.py to train the model.")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SIGN LANGUAGE RECOGNITION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    results = {
        "Data Integrity": test_data_integrity(),
        "Data Loading": test_data_loading(),
        "Extract Keypoints": test_extract_keypoints(),
        "Model Files": test_model_files()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYou can now:")
        print("1. Run 'python trainmodel.py' to train the model (if not already trained)")
        print("2. Run 'python app.py' for real-time prediction with OpenCV")
        print("3. Run 'python app2.py' for real-time prediction with Tkinter GUI")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease fix the issues before running the application.")
    print("=" * 60)

if __name__ == "__main__":
    main()
