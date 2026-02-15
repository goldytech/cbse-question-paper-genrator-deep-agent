"""Input File Locator package.

This package provides tools for locating and validating blueprint JSON files
from teacher input or auto-discovering from the input/classes/ folder structure.
"""

from .tool import locate_blueprint_tool

__all__ = ["locate_blueprint_tool"]
