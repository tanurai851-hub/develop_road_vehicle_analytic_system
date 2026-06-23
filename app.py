import argparse
import logging
import os
import sys
import time

# ─── PATH MANAGEMENT FOR LOCAL & RENDER CLOUD ───────────────────────
# Get the root directory of the project
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
# ───────────────────────────────────────────────────────────────────

from flask import Flask, Response, jsonify, render_template_string

# Standardized imports that work everywhere
try:
    from src import config as Config
    from src import pipeline as Pipeline
except (ModuleNotFoundError, ImportError):
    try:
        from src.config import Config
        from src.pipeline import Pipeline
    except (ModuleNotFoundError, ImportError):
        import config as Config  # type: ignore
        import pipeline as Pipeline  # type: ignore
