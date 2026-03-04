import sys
import os

# project root → enables "core.app.x"
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core", "app"))
