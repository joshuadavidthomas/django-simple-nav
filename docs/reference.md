# Reference

For class attributes, method signatures, and type information, see the [API Reference](apidocs/index.rst).

This page documents the runtime behaviors that aren't captured in the API docs.

## Template Tag

```htmldjango
{% load django_simple_nav %}
{% django_simple_nav nav [template_name="..."] %}
```

| Argument | Required | Description |
|---|---|---|
| `nav` | yes | A dotted import path string to a `Nav` class (e.g. `"config.nav.MainNav"`), a dotted path to a callable that accepts `request` and returns a `Nav` (e.g. `"config.nav.main_nav"`), or a `Nav` instance from the template context. See [Programmatic Navigation](usage.md#programmatic-navigation). |
| `template_name` | no | Override the template used to render the navigation. Passed as a keyword argument: `template_name="my_template.html"`. |

Expects `request` in the template context.

## Jinja2 Function

See [Jinja2](usage.md#jinja2) for setup and usage.

```python
def django_simple_nav(nav: str | Nav, template_name: str | None = None) -> str:
    ...
```

Same arguments as the template tag. Must be registered in the Jinja2 environment's `globals`.

## Template Resolution

`Nav.render()` resolves the template through these methods, in order:

| Method | Default behavior | Override to… |
|---|---|---|
| `get_template(template_name=None)` | Calls `get_template_name()` and loads the template from disk. | Return an inline template string, add caching, or customize loading. |
| `get_template_name()` | Returns `self.template_name` or raises `ImproperlyConfigured`. | Choose a template dynamically at runtime. |

If `get_template()` returns a string instead of a template object, `render()` compiles it as an inline template using the configured template engine.

See [Customizing Template Resolution](usage.md#customizing-template-resolution) for examples.

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
| `"is_anonymous"`, `"is_authenticated"`, `"is_active"`, `"is_staff"`, `"is_superuser"` | Read as a boolean attribute on `request.user`. |
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
