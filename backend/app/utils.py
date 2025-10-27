"""
Utility functions for HCM Chatbot
"""

import sys
import io
import os


def setup_utf8_encoding():
    """
    Setup UTF-8 encoding for Windows console output.
    This prevents UnicodeEncodeError when printing Vietnamese characters.
    """
    # Set environment variable for UTF-8 - this is the safest way
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def safe_print(*args, **kwargs):
    """
    Safe print that handles encoding issues on Windows.
    Replaces non-ASCII characters with ASCII equivalents.
    """
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        # If encoding fails, convert to ASCII-safe strings
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace problematic characters
                safe_arg = arg.encode('ascii', errors='replace').decode('ascii')
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))
        original_print(*safe_args, **kwargs)


# Store original print
original_print = print

# Override print if on Windows
if sys.platform == 'win32':
    print = safe_print
    setup_utf8_encoding()
