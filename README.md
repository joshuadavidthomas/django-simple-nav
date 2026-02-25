# django-simple-nav

<!-- intro-start -->
[![PyPI](https://img.shields.io/pypi/v/django-simple-nav)](https://pypi.org/project/django-simple-nav/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-simple-nav)
![Django Version](https://img.shields.io/badge/django-4.2%20%7C%205.2%20%7C%206.0-%2344B78B?labelColor=%23092E20)
<!-- https://shields.io/badges -->
<!-- django-4.2 | 5.2 | 6.0-#44B78B -->
<!-- labelColor=%23092E20 -->

`django-simple-nav` is a Python/Django application designed to simplify the integration of navigation and menu bars in your Django projects. With a straightforward API and customizable options, you can easily add and manage navigational elements in your web applications. It is designed to be simple to start with, but flexible enough to handle complex navigation structures while maintaining that same simplicity.

## Requirements

- Python 3.10, 3.11, 3.12, 3.13, 3.14
- Django 4.2, 5.2, 6.0

## Installation

<!-- getting-started-start -->
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

<!-- getting-started-end -->

## Getting Started

<!-- usage-start -->
1. **Create a navigation definition.**

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
    - `NavItem`: A single navigation item. It has two required and three optional attributes:
      - `title`: The title of the item.
      - `url`: The URL of the item. This can be a URL string (e.g. `https://example.com/about/` or `/about/`) or a Django URL name (e.g. `about-view`).
      - `permissions` (optional): A list of permissions that control the visibility of the item. These permissions can be `User` attributes (e.g. `is_authenticated`, `is_staff`, `is_superuser`), Django permissions (e.g. `myapp.django_perm`), or a callable that takes an `HttpRequest` and returns a `bool`.
      - `extra_context` (optional): A dictionary of additional context to pass to the template when rendering the navigation.
      - `append_slash` (optional): Controls whether a trailing slash is appended to the URL. Defaults to `None`, which falls back to `settings.APPEND_SLASH`. Set to `False` to prevent appending a slash, useful for URLs that must not end with a slash (e.g. Django Ninja's `/docs` or `/openapi.json`).

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

2. **Create a template for the navigation.**

    Create a template to render the navigation structure. This is a standard Django or Jinja 2 template so you can use any template features you like.

    The template will be passed an `items` variable in the context representing the structure of the navigation, containing the `NavItem` and `NavGroup` objects defined in your navigation.

    Any items with permissions attached will automatically filtered out before rendering the template based on the request user's permissions, so you don't need to worry about that in your template.

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

3. **Integrate navigation in templates.**:

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

After configuring your navigation, you can use it across your Django project by calling the `django_simple_nav` template tag in your templates. This tag dynamically renders navigation based on your defined structure, ensuring a consistent and flexible navigation experience throughout your application.
<!-- usage-end -->

## Examples

The [`example`](example/) directory contains a simple Django project that demonstrates how to use `django-simple-nav`. The example project includes a navigation definitions for a few different scenarios as well as some popular CSS frameworks.

You can run the example project by following these steps. These steps assume you have `git` and `python` installed on your system and are using a Unix-like shell. If you are using Windows, you may need to adjust the commands accordingly.

1. **Clone the repository.**

    ```bash
    git clone https://github.com/westerveltco/django-simple-nav
    cd django-simple-nav
    ```

2. **Create a new virtual environment, activate it, and install `django-simple-nav`.**

    ```bash
    python -m venv venv
    source venv/bin/activate
    python -m pip install .
    ```

3. **Run the example project.**

    ```bash
    python example/demo.py
    ```

4. **Open your browser to `http://localhost:8000` to see the examples in action.**

## Documentation

Please refer to the [documentation](https://django-simple-nav.westervelt.dev/) for more information.

## License

`django-simple-nav` is licensed under the MIT license. See the [`LICENSE`](LICENSE) file for more information.
