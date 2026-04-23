#!/usr/bin/env python3
import sys

def test_imports():
    try:
        import ROOT
        print("✅ Successfully imported ROOT")
    except ImportError as e:
        print(f"❌ Failed to import ROOT: {e}")
        return 1

    try:
        import trig_egamma_frame
        print("✅ Successfully imported trig_egamma_frame")
    except ImportError as e:
        print(f"❌ Failed to import trig_egamma_frame: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(test_imports())
