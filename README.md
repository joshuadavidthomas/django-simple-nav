# django-simple-nav

<!-- docs-intro-start -->
[![PyPI](https://img.shields.io/pypi/v/django-simple-nav)](https://pypi.org/project/django-simple-nav/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-simple-nav)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.2%20%7C%206.0-%2344B78B?labelColor=%23092E20)
<!-- https://shields.io/badges -->
<!-- django-4.2 | 5.2 | 6.0-#44B78B -->
<!-- labelColor=%23092E20 -->
Define your navigation in Python, render it in templates. `django-simple-nav` handles URL resolution, active state detection, and permission filtering so your nav stays in sync with your project.
<!-- docs-intro-end -->

<!-- docs-requirements-start -->
## Requirements

- Python 3.10, 3.11, 3.12, 3.13, 3.14
- Django 4.2, 5.2, 6.0
<!-- docs-requirements-end -->

<!-- docs-installation-start -->
## Installation

```bash
uv add django-simple-nav
# or
python -m pip install django-simple-nav
```

Add `django_simple_nav` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...,
    "django_simple_nav",
    # ...,
]
```
<!-- docs-installation-end -->

## Getting Started

Define your navigation in a Python file. `items` is what gets rendered, and `template_name` points to the template that controls the markup:

```python
# config/nav.py
from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem


class MainNav(Nav):
    template_name = "main_nav.html"
    items = [
        NavItem(title="Home", url="/"),
        NavItem(title="About", url="/about/"),
        NavGroup(
            title="Resources",
            items=[
                NavItem(title="Blog", url="/blog/"),
                NavItem(title="Contact", url="/contact/"),
            ],
        ),
    ]
```

Create `main_nav.html`. The template receives the `items` defined above — each has a `title`, `url`, `active` state, and groups have nested `items`:

```htmldjango
<!-- main_nav.html -->
<nav>
  <ul>
    {% for item in items %}
      <li>
        <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}>
          {{ item.title }}
        </a>
        {% if item.items %}
          <ul>
            {% for subitem in item.items %}
              <li>
                <a href="{{ subitem.url }}"{% if subitem.active %} class="active"{% endif %}>
                  {{ subitem.title }}
                </a>
              </li>
            {% endfor %}
          </ul>
        {% endif %}
      </li>
    {% endfor %}
  </ul>
</nav>
```

Then use the template tag wherever you want the nav to appear. The string is the import path to your `Nav` class:

```htmldjango
{% load django_simple_nav %}

{% django_simple_nav "config.nav.MainNav" %}
```

## Examples

The [`example`](example/) directory contains a simple Django project that demonstrates how to use `django-simple-nav`, including navigation definitions for a few different scenarios and some popular CSS frameworks.

```bash
git clone https://github.com/joshuadavidthomas/django-simple-nav
cd django-simple-nav
uv sync
uv run example/demo.py runserver
```

Then open your browser to `http://localhost:8000`.

## Documentation

For the full documentation — including permissions, extra context, Jinja2 support, self-rendering items, and more — please visit the [documentation site](https://django-simple-nav.joshthomas.dev/).

## License

`django-simple-nav` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
