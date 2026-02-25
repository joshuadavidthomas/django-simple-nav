# Usage

## Overview

`django-simple-nav` provides three classes for defining navigation:

- **`Nav`** — The top-level container. Defines a `template_name` and a list of `items`.
- **`NavItem`** — A single navigation link with a `title` and `url`.
- **`NavGroup`** — A group of items. Can have its own `url` or act as a non-linking container.

All three are imported from `django_simple_nav.nav`:

```python
from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem
```

## Defining a Navigation

Create a subclass of `Nav` with a `template_name` and a list of `items`:

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
            url="/resources/",
            items=[
                NavItem(title="Blog", url="/blog/"),
                NavItem(title="Contact", url="/contact/"),
            ],
        ),
        NavGroup(
            title="More",
            items=[
                NavItem(title="FAQ", url="/faq/"),
            ],
        ),
    ]
```

A `NavGroup` with a `url` acts as both a link and a container. Without a `url`, it's just a container (useful for dropdown menus or sections).

You can place this file anywhere in your Django project as long as it's importable. A common convention is a `nav.py` file next to your `settings.py`.

## URLs

`NavItem` and `NavGroup` support several URL formats:

```python
# A relative path
NavItem(title="About", url="/about/")

# An absolute URL
NavItem(title="GitHub", url="https://github.com/example")

# A Django URL name — resolved via reverse()
NavItem(title="Profile", url="user-profile")

# A callable — called with no arguments
NavItem(title="Profile", url=lambda: reverse("user-profile", args=[42]))

# reverse_lazy — useful at module level
NavItem(title="Profile", url=reverse_lazy("user-profile"))
```

When a string is given, `django-simple-nav` first tries `django.urls.reverse()`. If that raises `NoReverseMatch`, the string is used as a literal URL.

### Trailing Slashes

By default, `django-simple-nav` respects your `APPEND_SLASH` setting. You can override this per item:

```python
# Never append a slash, regardless of APPEND_SLASH
NavItem(title="API Docs", url="api-docs", append_slash=False)

# Always append a slash
NavItem(title="Blog", url="/blog", append_slash=True)
```

This is useful for URLs that must not end with a slash, such as Django Ninja's `/docs` or `/openapi.json`.

## Writing a Navigation Template

The template specified by `Nav.template_name` receives an `items` list in its context. Each item in the list exposes:

| Variable | Type | Description |
|---|---|---|
| `title` | `SafeString` | The item's title (can contain HTML) |
| `url` | `str` | The resolved URL (empty string for a `NavGroup` with no URL) |
| `active` | `bool` | Whether the item matches the current request URL |
| `items` | `list \| None` | Child items for `NavGroup`; `None` for `NavItem` |

Any keys from [`extra_context`](#extra-context) are also available directly on the item.

Here's a basic template:

````{tab} Django
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
````

````{tab} Jinja2
```jinja
<!-- main_nav.html.j2 -->
<ul>
  {% for item in items %}
    <li>
      <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}>
        {{ item.title }}
      </a>
      {% if item['items'] %}
        <ul>
          {% for subitem in item['items'] %}
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

In Jinja2 templates, use `item['items']` (bracket notation) to access child items. `item.items` in Jinja2 refers to the dict `.items()` method.
````

## Using the Template Tag

The `django_simple_nav` template tag (or Jinja2 function) renders a navigation into your template.

### Basic usage

Pass the import path to your `Nav` subclass as a string:

````{tab} Django
```htmldjango
{% load django_simple_nav %}

<nav>
  {% django_simple_nav "config.nav.MainNav" %}
</nav>
```
````

````{tab} Jinja2
```html
<nav>
  {{ django_simple_nav("config.nav.MainNav") }}
</nav>
```
````

### Passing a Nav instance

You can also pass a `Nav` instance from your view context:

```python
# views.py
from config.nav import MainNav


def example_view(request):
    return render(request, "example.html", {"nav": MainNav()})
```

````{tab} Django
```htmldjango
{% load django_simple_nav %}

<nav>
  {% django_simple_nav nav %}
</nav>
```
````

````{tab} Jinja2
```html
<nav>
  {{ django_simple_nav(nav) }}
</nav>
```
````

### Overriding the template

Pass a second argument to render the same navigation with a different template. This is useful for reusing a navigation definition in multiple places (e.g. a header and a footer):

````{tab} Django
```htmldjango
{% load django_simple_nav %}

<header>
  {% django_simple_nav "config.nav.MainNav" %}
</header>

<footer>
  {% django_simple_nav "config.nav.MainNav" "footer_nav.html" %}
</footer>
```
````

````{tab} Jinja2
```html
<header>
  {{ django_simple_nav("config.nav.MainNav") }}
</header>

<footer>
  {{ django_simple_nav("config.nav.MainNav", "footer_nav.html.j2") }}
</footer>
```
````

## Permissions

Permissions control which items are visible to the current user. Pass a list to the `permissions` parameter — **all** permissions in the list must pass for the item to be shown (AND logic).

```python
NavItem(title="Dashboard", url="/dashboard/", permissions=["is_authenticated"])
```

Four types of permissions are supported:

### User attribute checks

Checks a boolean attribute on `request.user`:

```python
permissions=["is_authenticated"]
permissions=["is_staff"]
permissions=["is_superuser"]
```

```{note}
Superusers short-circuit all permission checks — if the user is a superuser, the item is always visible regardless of other permissions in the list.
```

### Django permissions

Standard Django permission strings, checked via `user.has_perm()`:

```python
permissions=["myapp.view_post"]
permissions=["myapp.change_post", "myapp.delete_post"]  # user must have BOTH
```

### Callable permissions

Any callable that takes an `HttpRequest` and returns a `bool`:

```python
from django.http import HttpRequest


def is_beta_user(request: HttpRequest) -> bool:
    return hasattr(request.user, "profile") and request.user.profile.is_beta


NavItem(title="Beta Feature", url="/beta/", permissions=[is_beta_user])
```

### Combining permissions

Since permissions use AND logic, you can combine different types:

```python
# User must be authenticated AND have the Django permission
NavItem(
    title="Admin Panel",
    url="/admin/",
    permissions=["is_authenticated", "myapp.access_admin"],
)
```

For OR logic, use a callable:

```python
def is_staff_or_beta(request: HttpRequest) -> bool:
    return request.user.is_staff or is_beta_user(request)


NavItem(title="Feature", url="/feature/", permissions=[is_staff_or_beta])
```

### Permissions on groups

Permissions work the same way on `NavGroup`. Additionally, a `NavGroup` without a `url` will automatically hide itself if all of its children are filtered out by permissions — even if the group itself has no permissions defined.

```{note}
If `django.contrib.auth` is not in your `INSTALLED_APPS`, all permission checks are skipped and every item is shown regardless of its `permissions` list.
```

## Extra Context

Pass additional data to your templates with `extra_context`:

```python
NavItem(
    title="Blog",
    url="/blog/",
    extra_context={"icon": "book", "badge_count": 3},
)
NavGroup(
    title="Settings",
    items=[...],
    extra_context={"icon": "gear"},
)
```

Extra context keys are available directly on the item in templates:

```htmldjango
<a href="{{ item.url }}">
  {% if item.icon %}<span class="icon-{{ item.icon }}"></span>{% endif %}
  {{ item.title }}
  {% if item.badge_count %}<span class="badge">{{ item.badge_count }}</span>{% endif %}
</a>
```

The keys `title`, `url`, `active`, and `items` are reserved and cannot be overridden by `extra_context`.

## Active State Detection

Each item has an `active` property that indicates whether it matches the current request URL. This is determined automatically — you don't need to set it yourself.

The matching rules are:

- **Exact path match** — the item's resolved URL path must match the request path exactly. There is no prefix matching.
- **Query parameters** — if the item's URL includes query parameters, those must also match exactly.
- **Scheme and host** — for absolute URLs (e.g. `https://example.com/about/`), the scheme and host must match the request. Relative URLs only compare the path.

For `NavGroup`, `active` is `True` if the group's own URL matches **or** if any of its children (recursively) are active.

```htmldjango
<a href="{{ item.url }}"{% if item.active %} aria-current="page"{% endif %}>
  {{ item.title }}
</a>
```

## Self-Rendering Items

`NavItem` and `NavGroup` can render themselves, similar to Django's `{{ form }}`. Instead of manually writing the HTML for each item, use `{{ item }}` in your template:

```htmldjango
<nav>
  <ul>
    {% for item in items %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
</nav>
```

Each item renders using its own template:

- `NavItem` uses `django_simple_nav/navitem.html`
- `NavGroup` uses `django_simple_nav/navgroup.html`

These are minimal, semantic HTML templates that ship with the package. Self-rendering and dict-style access (`{{ item.title }}`, `{{ item.url }}`, etc.) work side by side.

### Custom templates per item

Override the template on an instance or subclass:

```python
# Per instance
NavItem(title="Home", url="/", template_name="myapp/custom_item.html")

# Per subclass
class DropdownNavGroup(NavGroup):
    template_name = "myapp/dropdown.html"
```

You can also call `render()` directly:

```python
item = NavItem(title="Home", url="/")
html = item.render(request)
```

```{note}
Self-rendering requires the default templates to be discoverable by Django's template loader. If you have `APP_DIRS = True` in your `TEMPLATES` setting (the default), this works automatically. If `APP_DIRS = False`, you can still use dict-style access — the default templates are only needed when `{{ item }}` is used.
```

## Settings

`django-simple-nav` has one optional setting:

```python
DJANGO_SIMPLE_NAV = {
    "TEMPLATE_BACKEND": None,  # default
}
```

**`TEMPLATE_BACKEND`** — The template backend to use when rendering navigations. Accepts a full backend path string (e.g. `"django.template.backends.django.DjangoTemplates"`). When set to `None` (the default), the first configured template backend is used. This is only relevant if your project has multiple template backends configured.
