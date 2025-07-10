#!/usr/bin/env python3

import sys
print("Python path:", sys.path)
print("Python version:", sys.version)

try:
    import flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print("✗ Flask import failed:", e)

try:
    import torch
    print("✓ PyTorch imported successfully")
except ImportError as e:
    print("✗ PyTorch import failed:", e)

try:
    import whisper
    print("✓ Whisper imported successfully")
except ImportError as e:
    print("✗ Whisper import failed:", e)

try:
    import moviepy
    print("✓ MoviePy imported successfully")
except ImportError as e:
    print("✗ MoviePy import failed:", e)

try:
    import moviepy.editor
    print("✓ MoviePy.editor imported successfully")
except ImportError as e:
    print("✗ MoviePy.editor import failed:", e)