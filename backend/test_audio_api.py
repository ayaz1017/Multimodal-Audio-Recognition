#!/usr/bin/env python
"""Test script for audio API endpoint"""

import requests
import json
import os
from pathlib import Path

# Test configuration
API_URL = 'http://localhost:5000/api/recognize_audio'
TEST_FILE = 'uploads/test_audio.wav'
BACKEND_DIR = Path(__file__).parent

def test_audio_endpoint():
    """Test the audio recognition endpoint"""
    
    # Check if test file exists
    test_path = BACKEND_DIR / TEST_FILE
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False
    
    print(f"📁 Testing with file: {test_path}")
    print(f"📊 File size: {test_path.stat().st_size} bytes")
    
    try:
        # Open and send file
        with open(test_path, 'rb') as f:
            files = {'file': f}
            print(f"🚀 Sending request to {API_URL}...")
            
            response = requests.post(API_URL, files=files, timeout=30)
        
        print(f"\n📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Audio processing completed")
            print(f"\n📊 Results:")
            print(f"  - Audio Features Extracted: Yes")
            print(f"  - MFCC Dimensions: {len(data.get('audio_features', {}).get('mfcc', []))}")
            print(f"  - Duration: {data.get('audio_features', {}).get('duration', 'N/A')} seconds")
            print(f"  - Sample Rate: {data.get('audio_features', {}).get('sample_rate', 'N/A')} Hz")
            print(f"  - Prediction: {data.get('predictions', {}).get('prediction', 'N/A')}")
            print(f"  - Confidence: {data.get('predictions', {}).get('probability', 'N/A'):.2%}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not reach backend at http://localhost:5000")
        print("   Make sure backend is running: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Backend took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    os.chdir(BACKEND_DIR)
    print("=" * 60)
    print("🎵 Audio Recognition API Test")
    print("=" * 60)
    success = test_audio_endpoint()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - check errors above")
