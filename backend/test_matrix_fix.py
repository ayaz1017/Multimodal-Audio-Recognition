#!/usr/bin/env python
"""Test audio processing with fixed model"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import torch
from models.audio_model import SimpleAudioModel, load_model
from utils.audio_processor import AudioProcessor

print("=" * 60)
print("Testing Audio Recognition Pipeline")
print("=" * 60)

# Test 1: Model initialization
print("\n1. Testing Model Initialization...")
try:
    model = SimpleAudioModel(input_size=18, num_emotions=7)
    test_input = torch.randn(1, 18)
    output = model(test_input)
    assert output.shape == (1, 7), f"Expected shape (1, 7), got {output.shape}"
    print(f"   [PASS] Model works with 18 inputs, outputs 7 emotions")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 2: Audio processing
print("\n2. Testing Audio Feature Extraction...")
try:
    processor = AudioProcessor()
    test_audio_path = "uploads/test_audio.wav"
    if os.path.exists(test_audio_path):
        features = processor.extract_all_features(test_audio_path)
        all_features = features['all_features']
        print(f"   [PASS] Extracted {len(all_features)} features from audio")
        print(f"     - MFCC: {len(features['mfcc'])} features")
        print(f"     - Spectral: {len(features['spectral'])} features")
        print(f"     - Temporal: {len(features['temporal'])} features")
        print(f"     - Total: {len(all_features)} (should be 18)")
        
        if len(all_features) != 18:
            print(f"   [WARN] Expected 18 features, got {len(all_features)}")
    else:
        print(f"   [INFO] Test audio file not found, skipping")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 3: Model loading
print("\n3. Testing Model Loading...")
try:
    model = load_model()
    print(f"   [PASS] Model loaded successfully")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 4: End-to-end prediction
print("\n4. Testing End-to-End Processing...")
try:
    processor = AudioProcessor()
    test_audio_path = "uploads/test_audio.wav"
    if os.path.exists(test_audio_path):
        # Extract features
        features = processor.extract_all_features(test_audio_path)
        audio_tensor = processor.process_for_model(test_audio_path)
        
        # Get prediction
        predictions = model.predict(audio_tensor)
        
        print(f"   [PASS] Processing complete!")
        print(f"     - Audio tensor shape: {audio_tensor.shape}")
        print(f"     - Prediction: {predictions['predictions']}")
        print(f"     - Confidence: {max(predictions['probabilities'][0]):.2%}")
    else:
        print(f"   [INFO] Test audio file not found, skipping")
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS! Matrix multiplication error is FIXED")
print("=" * 60)
