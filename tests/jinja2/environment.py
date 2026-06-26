"""Sets up a reasonably minimal Jinja2 environment for testing"""

from __future__ import annotations

from jinja2 import Environment
from jinja2 import FileSystemLoader

from django_simple_nav.jinja2 import django_simple_nav

# Ensure the same template paths are valid for both Jinja2 and Django templates
loader = FileSystemLoader("tests/jinja2/")

environment = Environment(loader=loader, trim_blocks=True)  # noqa: S701
environment.globals.update({"django_simple_nav": django_simple_nav})
