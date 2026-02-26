# Examples

This directory contains a self-contained Django project that demonstrates how to use `django-simple-nav`.

## Quick Start

From the root of the repository:

```bash
uv sync
uv run example/demo.py runserver
```

Then open your browser to `http://localhost:8000` to see the examples in action.

> [!NOTE]
> All navigation classes are defined in [`example/navigation.py`](navigation.py). This is a good place to start when exploring how each example works.

## What's Included

### Basic

A minimal navigation bar using plain HTML. Shows the core workflow: define a `Nav` class with `NavItem` and `NavGroup` entries, point it at a template, and render it with the `{% django_simple_nav %}` template tag. Demonstrates active state detection and groups with optional URLs.

### Permissions

Shows how to conditionally display nav items based on user permissions. Includes examples of built-in permission checks (`is_authenticated`, `is_staff`, `is_superuser`), Django permissions (`demo_permission`), and callable permission functions that receive the request.

### Extra Context

Demonstrates passing arbitrary extra data to nav items via the `extra_context` keyword argument and accessing that data in the nav template (e.g., setting a `data-foo` attribute).

### Nested Nav

Shows how to embed one `Nav` inside another by calling `{% django_simple_nav %}` within a nav template. The `NestedNav` class inherits from `BasicNav` and uses a template that renders `BasicNav` as a nested navigation.

### CSS Framework Integrations

Each of these demonstrates a nav styled for a popular CSS framework:

- **Tailwind CSS** — A responsive navbar using Alpine.js for interactivity, with a separate profile dropdown nav (`TailwindMainNav` + `TailwindProfileNav`).
- **Bootstrap 4** — A collapsible navbar with a dropdown menu, demonstrating `extra_context` for a disabled state.
- **Bootstrap 5** — Same structure as Bootstrap 4, adapted for Bootstrap 5's markup.
- **Pico CSS** — A clean, minimal navbar using Pico CSS's classless styling approach.

## Project Structure

```
example/
├── demo.py              # Django settings, views, and URL configuration
├── navigation.py        # All Nav class definitions
└── templates/
    ├── base.html        # Base template (index page with example list)
    ├── basic.html
    ├── bootstrap4.html
    ├── bootstrap5.html
    ├── extra_context.html
    ├── nested.html
    ├── permissions.html
    ├── picocss.html
    ├── tailwind.html
    └── navs/            # Nav-specific templates rendered by each Nav class
        ├── basic.html
        ├── bootstrap4.html
        ├── bootstrap5.html
        ├── example_list.html
        ├── extra_context.html
        ├── nested.html
        ├── picocss.html
        ├── tailwind_main.html
        └── tailwind_profile.html
```

## Documentation

For the full documentation — including permissions, extra context, Jinja2 support, self-rendering items, and more — please visit the [documentation site](https://django-simple-nav.westervelt.dev/).
