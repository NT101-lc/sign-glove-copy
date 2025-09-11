#!/usr/bin/env python3
"""
Test script to verify the single-hand gesture prediction model works correctly.
"""

import sys
import os
sys.path.append('backend')

from backend.core.model import predict_gesture

def test_single_hand_model():
    """Test single-hand gesture prediction."""
    print("Testing single-hand model...")
    
    # Test with sample sensor data (11 values)
    test_data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
    
    result = predict_gesture(test_data)
    print(f"Single-hand result: {result}")
    
    return result.get("status") == "success"

if __name__ == "__main__":
    print("=== Single-Hand Model Test ===")
    
    success = test_single_hand_model()
    
    print(f"\n=== Test Results ===")
    print(f"Single-hand model: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 Model test passed! Single-hand prediction is working correctly.")
    else:
        print("\n⚠️ Model test failed. Check model file and configuration.")
