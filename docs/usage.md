# Usage

## Creating a Navigation Definition

Define your navigation structure in a Python file. This file can be located anywhere in your Django project, provided it's importable. You can also split the navigations across multiple files if desired.

A good starting point is to create a single `nav.py` or `navigation.py` file in your Django project's main configuration directory (where your `settings.py` file is located).

`django-simple-nav` provides three classes to help you define your navigation structure:

- `Nav`: The main container for a navigation structure. It has two required attributes:
  - `template_name`: The name of the template to render the navigation structure.
  - `items`: A list of `NavItem` or `NavGroup` objects that represent the navigation structure.
- `NavGroup`: A container for a group of `NavItem` or `NavGroup` objects. It has two required and three optional attributes:
  - `title`: The title of the group.
  - `items`: A list of `NavItem` or `NavGroup`objects that represent the structure of the group.
  - `url` (optional): The URL of the group. If not provided, the group will not be a link but just a container for the items.
  - `permissions` (optional): A list of permissions that control the visibility of the group. These permissions can be `User` attributes (e.g. `is_authenticated`, `is_staff`, `is_superuser`), Django permissions (e.g. `myapp.django_perm`), or a callable that takes an `HttpRequest` and returns a `bool`.
  - `extra_context` (optional): A dictionary of additional context to pass to the template when rendering the navigation.
  - `template_name` (optional): The template used when the group renders itself via `{{ item }}`. Defaults to `django_simple_nav/navgroup.html`.
- `NavItem`: A single navigation item. It has two required and three optional attributes:
  - `title`: The title of the item.
  - `url`: The URL of the item. This can be a URL string (e.g. `https://example.com/about/` or `/about/`) or a Django URL name (e.g. `about-view`).
  - `permissions` (optional): A list of permissions that control the visibility of the item. These permissions can be `User` attributes (e.g. `is_authenticated`, `is_staff`, `is_superuser`), Django permissions (e.g. `myapp.django_perm`), or a callable that takes an `HttpRequest` and returns a `bool`.
  - `extra_context` (optional): A dictionary of additional context to pass to the template when rendering the navigation.
  - `append_slash` (optional): Controls whether a trailing slash is appended to the URL. Defaults to `None`, which falls back to `settings.APPEND_SLASH`. Set to `False` to prevent appending a slash, useful for URLs that must not end with a slash (e.g. Django Ninja's `/docs` or `/openapi.json`).
  - `template_name` (optional): The template used when the item renders itself via `{{ item }}`. Defaults to `django_simple_nav/navitem.html`.

Here's an example configuration:

```python
# config/nav.py
from django.http import HttpRequest

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem


def simple_permissions_check(request: HttpRequest) -> bool:
    return True


class MainNav(Nav):
    template_name = "main_nav.html"
    items = [
        NavItem(title="Relative URL", url="/relative-url"),
        NavItem(title="Absolute URL", url="https://example.com/absolute-url"),
        NavItem(title="Internal Django URL by Name", url="fake-view"),
        NavGroup(
            title="Group",
            url="/group",
            items=[
                NavItem(title="Relative URL", url="/relative-url"),
                NavItem(title="Absolute URL", url="https://example.com/absolute-url"),
                NavItem(title="Internal Django URL by Name", url="fake-view"),
            ],
        ),
        NavGroup(
            title="Container Group",
            items=[
                NavItem(title="Item", url="#"),
            ],
        ),
        NavItem(
            title="is_authenticated Item", url="#", permissions=["is_authenticated"]
        ),
        NavItem(title="is_staff Item", url="#", permissions=["is_staff"]),
        NavItem(title="is_superuser Item", url="#", permissions=["is_superuser"]),
        NavItem(
            title="myapp.django_perm Item", url="#", permissions=["myapp.django_perm"]
        ),
        NavItem(
            title="Item with callable permission",
            url="#",
            permissions=[simple_permissions_check],
        ),
        NavGroup(
            title="Group with Extra Context",
            items=[
                NavItem(
                    title="Item with Extra Context",
                    url="#",
                    extra_context={"foo": "bar"},
                ),
            ],
            extra_context={"baz": "qux"},
        ),
    ]
```

## Creating a Navigation Template

Create a template to render the navigation structure. This is a standard Django or Jinja2 template so you can use any template features you like.

The template will be passed an `items` variable in the context representing the structure of the navigation, containing the `NavItem` and `NavGroup` objects defined in your navigation.

Any items with permissions attached will automatically be filtered out before rendering the template based on the request user's permissions, so you don't need to worry about that in your template.

Items with extra context will have that context passed to the template when rendering the navigation, which you can access directly.

For example, given the above example `MainNav`, you could create a `main_nav.html` template:

```htmldjango
<!-- main_nav.html -->
<ul>
  {% for item in items %}
    <li>
      <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}{% if item.baz %} data-baz="{{ item.baz }}"{% endif %}>
        {{ item.title }}
      </a>
      {% if item.items %}
        <ul>
          {% for subitem in item.items %}
            <li>
              <a href="{{ subitem.url }}"{% if subitem.active %} class="active"{% endif %}{% if item.foo %} data-foo="{{ item.foo }}"{% endif %}>
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

The same template in Jinja would be written as follows:

```html
<!-- main_nav.html.j2 -->
<ul>
  {% for item in items %}
    <li>
      <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}{% if item.baz %} data-baz="{{ item.baz }}"{% endif %}>
        {{ item.title }}
      </a>
      {% if item['items'] %}
        <ul>
          {% for subitem in item['items'] %}
            <li>
              <a href="{{ subitem.url }}"{% if subitem.active %} class="active"{% endif %}{% if item.foo %} data-foo="{{ item.foo }}"{% endif %}>
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

Note that unlike in Django templates we need to index the `items` field as a string in Jinja.

## Integrating Navigation in Templates

Use the `django_simple_nav` template tag in your Django templates (the `django_simple_nav` function in Jinja) where you want to display the navigation.

For example:

```htmldjango
<!-- base.html -->
{% load django_simple_nav %}

{% block navigation %}
<nav>
  {% django_simple_nav "path.to.MainNav" %}
</nav>
{% endblock navigation %}
```

For Jinja:

```html
<!-- base.html.j2 -->
{% block navigation %}
<nav>
  {{ django_simple_nav("path.to.MainNav") }}
</nav>
{% endblock navigation %}
```

The template tag can either take a string representing the import path to your navigation definition or an instance of your navigation class:

```python
# example_app/views.py
from config.nav import MainNav


def example_view(request):
    return render(request, "example_app/example_template.html", {"nav": MainNav()})
```

```htmldjango
<!-- example_app/example_template.html -->
{% extends "base.html" %}
{% load django_simple_nav %}

{% block navigation %}
<nav>
    {% django_simple_nav nav %}
</nav>
{% endblock navigation %}
```

```html
<!-- example_app/example_template.html.j2 -->
{% extends "base.html" %}

{% block navigation %}
<nav>
    {{ django_simple_nav(nav) }}
</nav>
{% endblock navigation %}
```

Additionally, the template tag can take a second argument to specify the template to use for rendering the navigation. This is useful if you want to use the same navigation structure in multiple places but render it differently.

```htmldjango
<!-- base.html -->
{% load django_simple_nav %}

<footer>
  {% django_simple_nav "path.to.MainNav" "footer_nav.html" %}
</footer>
```

```html
<!-- base.html.j2 -->

<footer>
  {{ django_simple_nav("path.to.MainNav", "footer_nav.html.j2") }}
</footer>
```

## Self-Rendering Items

`NavItem` and `NavGroup` can render themselves, similar to how Django forms support `{{ form }}`. Instead of manually writing the HTML for each item, you can use `{{ item }}` in your template:

```htmldjango
<!-- main_nav.html -->
<nav>
  <ul>
    {% for item in items %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
</nav>
```

Each item renders using its own template — `django_simple_nav/navitem.html` for `NavItem` and `django_simple_nav/navgroup.html` for `NavGroup` by default. These are minimal, semantic HTML templates that ship with the package.

You can still use `{{ item.title }}`, `{{ item.url }}`, `{{ item.active }}`, and `{{ item.items }}` in your templates — self-rendering and dict-style access work side by side.

### Custom templates per item

You can customize how individual items render by setting `template_name`:

```python
# Per instance
NavItem(title="Home", url="/", template_name="myapp/custom_item.html")

# Per subclass
class DropdownNavGroup(NavGroup):
    template_name = "myapp/dropdown.html"
```

You can also call `render()` directly on any item:

```python
item = NavItem(title="Home", url="/")
html = item.render(request)
```

```{note}
The self-rendering feature requires the default templates to be discoverable by Django's template loader. If you have `APP_DIRS = True` in your `TEMPLATES` setting (the default), this works automatically. If you have `APP_DIRS = False`, you can still use dict-style access (`{{ item.title }}`, etc.) without any changes — the default templates are only loaded when `{{ item }}` is used.
```

After configuring your navigation, you can use it across your Django project by calling the `django_simple_nav` template tag in your templates. This tag dynamically renders navigation based on your defined structure, ensuring a consistent and flexible navigation experience throughout your application.
