# Getting Started

## Installation

1. **Install the package from PyPI.**

    ```bash
    python -m pip install django-simple-nav
    ```

2. **Add `django_simple_nav` to `INSTALLED_APPS`.**

    After installation, add `django_simple_nav` to your `INSTALLED_APPS` in your Django settings:

    ```python
    INSTALLED_APPS = [
        # ...,
        "django_simple_nav",
        # ...,
    ]
    ```

3. **Adjust your Django project's settings.**

    If you plan to use the permissions feature of `django-simple-nav` to filter your navigation items based on the `request.user`, `django.contrib.auth` and `django.contrib.contenttypes` must be added to your `INSTALLED_APPS` as well:

    ```python
    INSTALLED_APPS = [
        # ...,
        "django.contrib.auth",
        "django.contrib.contenttypes",
        # ...,
    ]
    ```

    If you do not add `django.contrib.auth` to your `INSTALLED_APPS` and you define any permissions for your navigation items, `django-simple-nav` will simply ignore the permissions and render all items regardless of whether the permission check is `True` or `False.`

### Jinja2

`django-simple-nav` can be used with the `django.template.backends.jinja2.Jinja2` template engine backend.

1. **Add the template function to your Jinja environment**

    ```python
    from jinja2 import Environment
    from jinja2 import FileSystemLoader

    from django_simple_nav.jinja2 import django_simple_nav

    environment = Environment()
    environment.globals.update({"django_simple_nav": django_simple_nav})
    ```

## Quick Example

Define your navigation in a Python file:

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

Create a template to render it:

```htmldjango
<!-- main_nav.html -->
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
```

Use the template tag in your templates:

```htmldjango
{% load django_simple_nav %}

<nav>
  {% django_simple_nav "config.nav.MainNav" %}
</nav>
```

See the [Usage](usage.md) page for the full API, including permissions, extra context, Jinja2 templates, self-rendering items, and more.
