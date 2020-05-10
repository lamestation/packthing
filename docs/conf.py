import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from packthing import __version__  # isort:skip


project = "packthing"
copyright = "2020, LameStation"
author = "LameStation"

release = __version__
version = __version__

extensions = []
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
