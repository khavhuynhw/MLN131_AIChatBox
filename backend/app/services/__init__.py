# Import utility for safe printing
import sys
if sys.platform == 'win32':
    from ..utils import safe_print, setup_utf8_encoding
    setup_utf8_encoding()
