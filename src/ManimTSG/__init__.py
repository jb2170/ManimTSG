from __future__ import annotations

"""Manim 'Tex String Groups' for hierarchical TeX / LaTeX"""

__version__ = "0.9.0"

from .TexStringGroup import tex_string_group, TexStringGroup
from .util import fqln, iter_interspersed

__all__ = [
    "tex_string_group",
    "TexStringGroup",
    "fqln",
    "iter_interspersed"
]
