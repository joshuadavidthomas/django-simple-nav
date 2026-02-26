# Getting Started

We'll add a navigation bar to a Django project — define the structure in Python, write a template, and render it.

This assumes you've already [installed](index.md#installation) the package and have a Django project with at least one view and template.

## Define a navigation

Create a file called `nav.py` next to your `settings.py`. The `items` list is what gets rendered, and `template_name` points to the template that controls the markup:

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

Now we need the `main_nav.html` that our `Nav` points to. The template receives the `items` we defined above — each has a `title`, `url`, and groups have nested `items`. Create it in your templates directory:

```htmldjango
<!-- main_nav.html -->
<nav>
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
</nav>
```

## Render the navigation

Now we can use the `django_simple_nav` template tag to render our navigation. Open your base template (or any template) and add:

```htmldjango
{% load django_simple_nav %}

{% django_simple_nav "config.nav.MainNav" %}
```

The string `"config.nav.MainNav"` is the import path to our `Nav` class.

Load a page in your browser — you should see an unstyled list with "Home", "About", and a "Resources" group containing "Blog" and "Contact".

## Highlight the active page

Each item also has an `active` property that's `True` when its URL matches the current request. Let's use it to highlight the current page:

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

Reload the page — the link for the current page will now have the `active` class. You can style it with CSS to make it stand out.

## Next steps

That's it — a navigation defined in Python, rendered in a template. From here you can:

- [Control which items are visible](usage.md#permissions) based on the user's permissions
- [Pass extra data to templates](usage.md#extra-context) for icons, badges, or other custom rendering
- [Use Jinja2 templates](usage.md#jinja2) instead of Django templates
- [Let items render themselves](usage.md#self-rendering-items) for less template boilerplate

See the [reference](reference.md) for full details on all attributes and behaviors.
