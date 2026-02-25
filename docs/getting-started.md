# Getting Started

We'll add a navigation bar to a Django project — define the structure in Python, write a template, and render it.

This assumes you have an existing Django project with at least one view and template.

## Install the package

```bash
python -m pip install django-simple-nav
```

Add it to `INSTALLED_APPS` in your settings:

```python
INSTALLED_APPS = [
    # ...,
    "django_simple_nav",
    # ...,
]
```

That's all the configuration we need to get started.

## Define a navigation

We'll create a simple navigation with a few links and a dropdown group. Create a file called `nav.py` next to your `settings.py`:

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

Notice the three building blocks: a `NavItem` is a single link, a `NavGroup` holds other items together, and the `Nav` ties them to a template.

## Create the template

Now we need the `main_nav.html` template that our `Nav` points to. Create it in your templates directory:

```htmldjango
<!-- main_nav.html -->
<ul>
  {% for item in items %}
    <li>
      <a href="{{ item.url }}">{{ item.title }}</a>
      {% if item.items %}
        <ul>
          {% for subitem in item.items %}
            <li><a href="{{ subitem.url }}">{{ subitem.title }}</a></li>
          {% endfor %}
        </ul>
      {% endif %}
    </li>
  {% endfor %}
</ul>
```

Notice that each item has a `title` and `url`, and groups have their own nested `items`.

## Render the navigation

Now we can use the `django_simple_nav` template tag to render our navigation. Open your base template (or any template) and add:

```htmldjango
{% load django_simple_nav %}

<nav>
  {% django_simple_nav "config.nav.MainNav" %}
</nav>
```

The string `"config.nav.MainNav"` is the import path to our `Nav` class.

Load a page in your browser — you should see an unstyled list with "Home", "About", and a "Resources" group containing "Blog" and "Contact".

## Highlight the active page

Let's improve the template to highlight whichever link matches the current page. Each item has an `active` property that's `True` when the item's URL matches the request:

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

Reload the page — the link for the current page will now have the `active` class. You can style it with CSS to make it stand out.

## Next steps

That's it — a navigation defined in Python, rendered in a template. From here you can:

- [Control which items are visible](usage.md#permissions) based on the user's permissions
- [Pass extra data to templates](usage.md#extra-context) for icons, badges, or other custom rendering
- [Use Jinja2 templates](usage.md#jinja2) instead of Django templates
- [Let items render themselves](usage.md#self-rendering-items) for less template boilerplate

See the [reference](reference.md) for full details on all attributes and behaviors.
