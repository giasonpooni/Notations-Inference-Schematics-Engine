"""Notations Inference Schematics Engine."""
from .compiler import compile_schematic, inspect_schematic
from .contracts import validate_catalog, validate_query, validate_schematic

__all__ = [
    "compile_schematic",
    "inspect_schematic",
    "validate_catalog",
    "validate_query",
    "validate_schematic",
]
__version__ = "0.1.0"
