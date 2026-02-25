# Reference

## Nav

The top-level navigation container. Subclassed to define a navigation structure.

| Attribute | Type | Description |
|---|---|---|
| `template_name` | `str` | Template used to render the navigation. Required. |
| `items` | `list[NavItem \| NavGroup]` | The navigation items. Required. |

**Methods:**

| Method | Description |
|---|---|
| `render(request, template_name=None)` | Renders the navigation to an HTML string. If `template_name` is given, it overrides the class attribute. |
| `get_items(request)` | Returns `items` filtered by each item's permissions. |
| `get_context_data(request)` | Returns the template context: `{"items": [...]}`. |

## NavItem

A single navigation link.

| Attribute | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | required | Display text. Treated as safe HTML. |
| `url` | `str \| Callable \| Promise \| None` | `None` | The URL. See [URL resolution](#url-resolution). |
| `permissions` | `list[str \| Callable]` | `[]` | Controls visibility. See [Permission evaluation](#permission-evaluation). |
| `extra_context` | `dict[str, object]` | `{}` | Additional template context. Cannot override `title`, `url`, `active`, or `items`. |
| `append_slash` | `bool \| None` | `None` | Controls trailing slash. `None` defers to `settings.APPEND_SLASH`. |
| `template_name` | `str \| None` | `None` | Template for self-rendering. Defaults to `django_simple_nav/navitem.html`. |

**Methods:**

| Method | Description |
|---|---|
| `render(request)` | Renders the item to an HTML string using its template. |
| `get_url()` | Returns the resolved URL string. |
| `get_active(request)` | Returns `True` if this item matches the current request. See [Active state](#active-state). |
| `check_permissions(request)` | Returns `True` if the current user passes all permissions. |
| `get_context_data(request)` | Returns `{"title": ..., "url": ..., "active": ..., "items": None, **extra_context}`. |

## NavGroup

A group of navigation items. Extends `NavItem`.

| Attribute | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | required | Display text. |
| `url` | `str \| Callable \| Promise \| None` | `None` | Optional URL. If omitted, the group is a non-linking container. Returns `""` instead of raising an error. |
| `items` | `list[NavItem \| NavGroup]` | `[]` | Child items. |
| `permissions` | `list[str \| Callable]` | `[]` | Controls visibility. |
| `extra_context` | `dict[str, object]` | `{}` | Additional template context. |
| `append_slash` | `bool \| None` | `None` | Controls trailing slash. |
| `template_name` | `str \| None` | `None` | Template for self-rendering. Defaults to `django_simple_nav/navgroup.html`. |

**Differences from `NavItem`:**

- `get_url()` returns `""` when no URL is set (instead of raising an error).
- `get_active(request)` returns `True` if the group's own URL matches **or** any child is active (recursive).
- `check_permissions(request)` also hides the group if it has no URL and all children are hidden by permissions.
- `get_items(request)` returns child items filtered by permissions.

## Template Tag

```htmldjango
{% load django_simple_nav %}
{% django_simple_nav nav [template_name] %}
```

| Argument | Required | Description |
|---|---|---|
| `nav` | yes | A dotted import path string (e.g. `"config.nav.MainNav"`) or a `Nav` instance from the template context. |
| `template_name` | no | Override the template used to render the navigation. |

Expects `request` in the template context.

## Jinja2 Function

See [Jinja2](usage.md#jinja2) for setup and usage.

```text
django_simple_nav(nav: str | Nav, template_name: str | None = None) -> str
```

Same arguments as the template tag. Must be registered in the Jinja2 environment's `globals`.

## Template Context

The template specified by `Nav.template_name` receives:

| Variable | Type | Description |
|---|---|---|
| `items` | `list` | Top-level navigation items. |

Each item in the list exposes:

| Variable | Type | Description |
|---|---|---|
| `title` | `SafeString` | The item's title. |
| `url` | `str` | Resolved URL. Empty string for a `NavGroup` without a URL. |
| `active` | `bool` | Whether this item matches the current request. |
| `items` | `list \| None` | Child items for `NavGroup`. `None` for `NavItem`. |
| *extra_context keys* | `object` | Any additional keys from `extra_context`. |

Items are also self-rendering: `{{ item }}` renders the item using its own template. See [Self-Rendering Items](usage.md#self-rendering-items).

## URL Resolution

When a `url` is provided, it is resolved in this order:

1. **`Promise`** (e.g. `reverse_lazy`): converted to a string.
2. **Callable**: called with no arguments; the return value is used.
3. **String**: passed to `django.urls.reverse()`. If `NoReverseMatch` is raised, the string is used as a literal URL.

After resolution, the trailing slash is adjusted based on `append_slash`:

- `None`: uses `settings.APPEND_SLASH`.
- `True`: always appends a slash to the path.
- `False`: never appends a slash to the path.

The slash logic applies only to the path component — query strings, fragments, and absolute URL schemes are preserved.

## Active State

An item is considered active when its resolved URL matches the current request.

| Condition | Rule |
|---|---|
| Path | Exact match only. No prefix matching. |
| Query parameters | Must match exactly (parsed as dictionaries). |
| Scheme and host | For absolute URLs, must match the request. Relative URLs compare only the path. |
| `NavGroup` | Active if its own URL matches **or** any descendant is active. |

## Permission Evaluation

See [Permissions](usage.md#permissions) for practical examples.

Permissions are evaluated in order. **All** must pass (AND logic).

| Permission type | How it's checked |
|---|---|
| `"is_authenticated"`, `"is_staff"`, `"is_superuser"` | Read as a boolean attribute on `request.user`. |
| `"app.codename"` (any other string) | Checked via `request.user.has_perm()`. |
| Callable | Called with `request`; must return `bool`. |

Special cases:

- **Superuser short-circuit**: if `request.user.is_superuser` is `True`, all permission checks pass immediately.
- **No `django.contrib.auth`**: all permission checks are skipped; every item is shown.
- **No `request.user`**: items with permissions are hidden; items without permissions are shown.

## Settings

```python
DJANGO_SIMPLE_NAV = {
    "TEMPLATE_BACKEND": None,  # default
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `TEMPLATE_BACKEND` | `str \| None` | `None` | Full path of the template backend to use (e.g. `"django.template.backends.django.DjangoTemplates"`). When `None`, the first configured backend is used. Only relevant with multiple template backends. |
