"""Thin engine wrapper for probes (imports ROOT/arena.py)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from arena import Arena  # noqa
