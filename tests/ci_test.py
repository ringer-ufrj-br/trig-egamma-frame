#!/usr/bin/env python3
import sys

try:
    import trig_egamma_frame
    print("✅ Successfully imported trig_egamma_frame")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Failed to import trig_egamma_frame: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠️ An unexpected error occurred during import: {e}")
    sys.exit(1)
