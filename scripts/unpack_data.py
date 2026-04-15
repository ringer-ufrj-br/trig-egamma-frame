#!/usr/bin/env python3
import tarfile
import os
import sys

def unpack_tgz(filepath, target_dir=None):
    """
    Unpacks a .tgz file to the specified target directory.
    If no target directory is specified, it unpacks in the same directory as the source file.
    """
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found at {filepath}")
        return

    if not filepath.endswith(".tgz") and not filepath.endswith(".tar.gz"):
        print(f"⚠️ Warning: File {filepath} does not have a standard .tgz extension.")

    if target_dir is None:
        target_dir = os.path.dirname(filepath)

    print(f"📦 Unpacking {filepath}...")
    print(f"📂 Extracting to {target_dir}...")

    try:
        with tarfile.open(filepath, "r:gz") as tar:
            tar.extractall(path=target_dir)
        print("✅ Extraction completed successfully!")
    except Exception as e:
        print(f"❌ An error occurred during extraction: {e}")

if __name__ == "__main__":
    archive_path = "/mnt/shared/storage03/projects/cern/data/mc21_13p6TeV/no_restrictions/user.isilvafe.mc21_13p6TeV.JF17.AOD.r14136_without_sigma_constraint_31.10.23_v0_EXT0.tap_jf17_5M_XYZ.root.tgz"
    
    # You can pass a different path as an argument if needed
    if len(sys.argv) > 1:
        archive_path = sys.argv[1]
        
    unpack_tgz(archive_path)
