# django-simple-nav

[![PyPI](https://img.shields.io/pypi/v/django-simple-nav)](https://pypi.org/project/django-simple-nav/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-simple-nav)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.2%20%7C%206.0-%2344B78B?labelColor=%23092E20)

Define your navigation in Python, render it in templates. `django-simple-nav` handles URL resolution, active state detection, and permission filtering so your nav stays in sync with your project.

## Installation

```bash
python -m pip install django-simple-nav
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...,
    "django_simple_nav",
    # ...,
]
```

If you're using the [permissions](usage.md#permissions) feature, you'll also need `django.contrib.auth` and `django.contrib.contenttypes` in `INSTALLED_APPS`.

For [Jinja2](usage.md#jinja2) support, see the setup guide.

## Requirements

- Python 3.10, 3.11, 3.12, 3.13, 3.14
- Django 4.2, 5.2, 6.0

## Next

Head to [Getting Started](getting-started.md) to build your first navigation.

```{toctree}
:hidden:
:maxdepth: 3

getting-started.md
usage.md
reference.md
changelog.md
```

```{toctree}
:hidden:
:maxdepth: 3
:caption: API Reference

apidocs/index.rst
apidocs/django_simple_nav/django_simple_nav.rst
```

```{toctree}
:hidden:
:maxdepth: 3
:caption: Development

development/contributing.md
development/just.md
Releasing <development/releasing.md>
```
