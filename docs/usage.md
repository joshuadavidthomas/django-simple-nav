# Usage

These guides cover specific features of `django-simple-nav`. If you're new to the library, start with [Getting Started](getting-started.md).

## Permissions

To control which navigation items a user can see, pass a `permissions` list. All permissions in the list must pass for the item to be shown.

```python
NavItem(title="Dashboard", url="/dashboard/", permissions=["is_authenticated"])
```

### User attribute checks

Use a string matching a boolean attribute on `request.user`:

```python
NavItem(title="Dashboard", url="/dashboard/", permissions=["is_authenticated"])
NavItem(title="Staff Area", url="/staff/", permissions=["is_staff"])
```

### Django permissions

Use standard Django permission strings:

```python
NavItem(title="Edit Posts", url="/posts/edit/", permissions=["blog.change_post"])
```

Multiple permissions require the user to have all of them:

```python
NavItem(
    title="Manage Posts",
    url="/posts/manage/",
    permissions=["blog.change_post", "blog.delete_post"],
)
```

### Callable permissions

Pass any callable that takes an `HttpRequest` and returns a `bool`:

```python
from django.http import HttpRequest


def is_beta_user(request: HttpRequest) -> bool:
    return hasattr(request.user, "profile") and request.user.profile.is_beta


NavItem(title="Beta Feature", url="/beta/", permissions=[is_beta_user])
```

### Combining permission types

You can mix types in a single list. All must pass:

```python
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

Permissions on a `NavGroup` work the same as on `NavItem`. If a `NavGroup` has no `url` and all of its children are hidden by permissions, the group hides itself automatically.

```python
NavGroup(
    title="Admin",
    permissions=["is_staff"],
    items=[
        NavItem(title="Users", url="/admin/users/", permissions=["auth.view_user"]),
        NavItem(
            title="Settings",
            url="/admin/settings/",
            permissions=["myapp.change_settings"],
        ),
    ],
)
```

## Extra Context

To pass additional data to your templates, use `extra_context`:

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

Access the values directly on the item in your template:

```htmldjango
<a href="{{ item.url }}">
  {% if item.icon %}<span class="icon-{{ item.icon }}"></span>{% endif %}
  {{ item.title }}
  {% if item.badge_count %}<span class="badge">{{ item.badge_count }}</span>{% endif %}
</a>
```

The keys `title`, `url`, `active`, and `items` are reserved and cannot be overridden by `extra_context`.

## Jinja2

`django-simple-nav` works with Django's Jinja2 template backend. Register the template function in your Jinja2 environment:

```python
from django_simple_nav.jinja2 import django_simple_nav

environment.globals.update({"django_simple_nav": django_simple_nav})
```

Then use it as a function call in your templates:

```jinja
<nav>
  {{ django_simple_nav("config.nav.MainNav") }}
</nav>
```

You can pass a `Nav` instance or override the template, just like the Django template tag:

```jinja
{{ django_simple_nav(nav) }}
{{ django_simple_nav("config.nav.MainNav", "footer_nav.html.j2") }}
```

In Jinja2 navigation templates, use bracket notation to access child items — `item['items']` instead of `item.items` — because `item.items` calls the dict `.items()` method in Jinja2:

```jinja
{% if item['items'] %}
  {% for subitem in item['items'] %}
    ...
  {% endfor %}
{% endif %}
```

## Overriding the Template at Render Time

To render the same navigation with a different template — say, a header and a footer with different markup — pass a second argument to the template tag:

```htmldjango
{% load django_simple_nav %}

<header>
  {% django_simple_nav "config.nav.MainNav" %}
</header>

<footer>
  {% django_simple_nav "config.nav.MainNav" "footer_nav.html" %}
</footer>
```

## Passing a Nav Instance from a View

Instead of an import path string, you can pass a `Nav` instance through your view context. This lets you construct the navigation dynamically:

```python
# views.py
from config.nav import MainNav


def example_view(request):
    return render(request, "example.html", {"nav": MainNav()})
```

```htmldjango
{% load django_simple_nav %}

<nav>
  {% django_simple_nav nav %}
</nav>
```

## Self-Rendering Items

Instead of writing the HTML for each item manually, you can use `{{ item }}` to let items render themselves:

```htmldjango
<nav>
  <ul>
    {% for item in items %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
</nav>
```

Each item renders using a default template — `django_simple_nav/navitem.html` for `NavItem` and `django_simple_nav/navgroup.html` for `NavGroup`. Self-rendering and dict-style access (`{{ item.title }}`, `{{ item.url }}`, etc.) work side by side.

To customize per item, set `template_name`:

```python
NavItem(title="Home", url="/", template_name="myapp/custom_item.html")
```

Or override it on a subclass:

```python
class DropdownNavGroup(NavGroup):
    template_name = "myapp/dropdown.html"
```

You can also call `render()` directly on any item:

```python
item = NavItem(title="Home", url="/")
html = item.render(request)
```

```{note}
Self-rendering requires the default templates to be discoverable by Django's template loader. With `APP_DIRS = True` (the default), this works automatically. With `APP_DIRS = False`, dict-style access still works — the default templates are only loaded when `{{ item }}` is used.
```
