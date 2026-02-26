# Tutorial

In this tutorial, we'll add navigation to the Django polls app — first by hand, then by refactoring to use `django-simple-nav`. By the end, you'll have a navigation bar with links, active page highlighting, and permission-based visibility, all defined in Python.

We're picking up where [Django's official polls tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/) leaves off. If you haven't gone through it, you'll need a working polls app with these views:

- **Polls list** — `polls:index`
- **Poll detail** — `polls:detail`
- **Poll results** — `polls:results`

You'll also need `django.contrib.auth` set up so you can log in to the admin.

## The starting point

Right now the polls app doesn't have any navigation. We'll add a nav bar to every page with these links:

- **Polls** — always visible, links to the polls list
- **Admin** — only visible to staff users
- **Log out** / **Log in** — changes based on whether the user is authenticated

Let's start by doing it the way you would without any library.

## Building navigation by hand

### Create a base template

We need a base template that every page extends. Create `templates/base.html`:

```htmldjango
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}Polls{% endblock %}</title>
  <style>
    nav { background: #333; padding: 10px; }
    nav a { color: white; margin-right: 15px; text-decoration: none; }
    nav a.active { font-weight: bold; text-decoration: underline; }
  </style>
</head>
<body>
  <nav>
    <a href="{% url 'polls:index' %}"
       {% if request.resolver_match.url_name == 'index' %}class="active"{% endif %}>
      Polls
    </a>
    {% if user.is_staff %}
      <a href="{% url 'admin:index' %}">Admin</a>
    {% endif %}
    {% if user.is_authenticated %}
      <a href="{% url 'admin:logout' %}">Log out</a>
    {% else %}
      <a href="{% url 'admin:login' %}">Log in</a>
    {% endif %}
  </nav>

  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

### Update the polls templates

Now update each polls template to extend the base. Open `polls/templates/polls/index.html`:

```htmldjango
{% extends "base.html" %}

{% block title %}Polls{% endblock %}

{% block content %}
  {% if latest_question_list %}
    <ul>
      {% for question in latest_question_list %}
        <li><a href="{% url 'polls:detail' question.id %}">{{ question.question_text }}</a></li>
      {% endfor %}
    </ul>
  {% else %}
    <p>No polls are available.</p>
  {% endif %}
{% endblock %}
```

Do the same for `polls/templates/polls/detail.html` and `polls/templates/polls/results.html` — wrap the existing content in `{% extends "base.html" %}` and `{% block content %}...{% endblock %}`.

### Check it in the browser

Run the development server and visit `http://localhost:8000/polls/`. You should see the "Polls" link in the nav bar, with "Admin" and "Log out" / "Log in" appearing based on your login state.

This works. But look at the nav markup in `base.html` — it mixes HTML structure, URL resolution, active state logic, and permission checks all in one place. If we wanted to add this same nav to a different template, we'd copy and paste the whole block. And every new link means more `{% if %}` / `{% url %}` logic woven into the HTML.

Let's clean this up.

## Refactoring with django-simple-nav

### Install the package

```bash
uv add django-simple-nav
# or
python -m pip install django-simple-nav
```

Add it to `INSTALLED_APPS` in your settings:

```python
INSTALLED_APPS = [
    # ...
    "django_simple_nav",
    # ...
]
```

### Define the navigation

Create a file called `polls/nav.py`:

```python
from django.http import HttpRequest

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavItem


def is_anonymous(request: HttpRequest) -> bool:
    return not request.user.is_authenticated


class PollsNav(Nav):
    template_name = "polls_nav.html"
    items = [
        NavItem(title="Polls", url="polls:index"),
        NavItem(title="Admin", url="admin:index", permissions=["is_staff"]),
        NavItem(
            title="Log out",
            url="admin:logout",
            permissions=["is_authenticated"],
        ),
        NavItem(
            title="Log in",
            url="admin:login",
            permissions=[is_anonymous],
        ),
    ]
```

Let's walk through what's happening here.

The URLs are **named URL patterns** — `"polls:index"`, `"admin:index"`, and so on. In our hand-written template, we had to use `{% url 'polls:index' %}` to resolve these. Here, `django-simple-nav` resolves them automatically. If a string matches a named URL pattern, it becomes the resolved path. If it doesn't match (like a literal `"/about/"` or `"#"`), it's used as-is.

The `permissions` argument controls who can see each item. When we pass `permissions=["is_staff"]`, `django-simple-nav` checks `request.user.is_staff` — if it's falsy, the item is filtered out before the template ever sees it. Same with `"is_authenticated"`. These string permissions work for any boolean attribute on the user object.

For the "Log in" link, we need the opposite — show it only when the user is *not* authenticated. That's what the `is_anonymous` function above the class is for. It takes the request and returns `True` when the user isn't logged in. Any callable that accepts an `HttpRequest` and returns a `bool` works as a permission — this is the intended way to handle conditions that go beyond checking a user attribute. Inverted checks, feature flags, time-based conditions, whatever you need — write a function and pass it in.

These are the three permission types: strings for user attributes (`"is_staff"`, `"is_superuser"`), strings for Django permissions (`"blog.change_post"`), and callables for custom logic. The [permissions guide](usage.md#permissions) goes deeper on all three.

### Create the nav template

Create `templates/polls_nav.html`:

```htmldjango
<nav>
  {% for item in items %}
    <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}>
      {{ item.title }}
    </a>
  {% endfor %}
</nav>
```

That's the entire nav template. No permission checks, no URL resolution — just a loop over items. `django-simple-nav` has already resolved the URLs and filtered out items the user can't see before the template renders.

### Update the base template

Now replace the hand-written nav in `templates/base.html`:

```htmldjango
{% load django_simple_nav %}

<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}Polls{% endblock %}</title>
  <style>
    nav { background: #333; padding: 10px; }
    nav a { color: white; margin-right: 15px; text-decoration: none; }
    nav a.active { font-weight: bold; text-decoration: underline; }
  </style>
</head>
<body>
  {% django_simple_nav "polls.nav.PollsNav" %}

  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

The `{% django_simple_nav "polls.nav.PollsNav" %}` tag loads our `PollsNav` class by its import path and renders it. The hand-written `{% if %}` blocks and `{% url %}` tags are gone.

### Try it out

Reload the page. The nav should look and behave exactly as before — "Polls" is always visible, "Admin" appears for staff users, and "Log out" / "Log in" toggles based on authentication.

But now the *what* (which links, which permissions) lives in `polls/nav.py`, and the *how it looks* lives in `polls_nav.html`. If you want a different nav on a different page, you define another `Nav` class. If you want the same nav with different markup, you pass a different template.

## Adding a group

Let's say we want to group some links together. We can add a "Results" dropdown under each poll. But for our simple polls nav, let's group the authentication links:

Update `polls/nav.py`:

```python
from django.http import HttpRequest

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem


def is_anonymous(request: HttpRequest) -> bool:
    return not request.user.is_authenticated


class PollsNav(Nav):
    template_name = "polls_nav.html"
    items = [
        NavItem(title="Polls", url="polls:index"),
        NavItem(title="Admin", url="admin:index", permissions=["is_staff"]),
        NavGroup(
            title="Account",
            items=[
                NavItem(
                    title="Log out",
                    url="admin:logout",
                    permissions=["is_authenticated"],
                ),
                NavItem(
                    title="Log in",
                    url="admin:login",
                    permissions=[is_anonymous],
                ),
            ],
        ),
    ]
```

And update `templates/polls_nav.html` to handle groups:

```htmldjango
<nav>
  {% for item in items %}
    {% if item.items %}
      <span>{{ item.title }}:
        {% for subitem in item.items %}
          <a href="{{ subitem.url }}"{% if subitem.active %} class="active"{% endif %}>
            {{ subitem.title }}
          </a>
        {% endfor %}
      </span>
    {% else %}
      <a href="{{ item.url }}"{% if item.active %} class="active"{% endif %}>
        {{ item.title }}
      </a>
    {% endif %}
  {% endfor %}
</nav>
```

Reload and you'll see "Account:" followed by either "Log out" or "Log in" depending on your login state. A `NavGroup` that has no visible children hides itself automatically, so the "Account" label won't appear as an orphan.

## What we built

Starting from the Django polls tutorial, we:

1. Built a navigation bar by hand — mixing URLs, permissions, and active state into template logic.
2. Installed `django-simple-nav` and moved the navigation structure into a Python class.
3. Replaced the hand-written template logic with a clean loop over pre-resolved, pre-filtered items.
4. Added a `NavGroup` to organize related links.

The navigation is now defined in one place, tested by one set of rules, and rendered by a template that only cares about markup.

## Alternatives

There are other ways to approach navigation in Django. Here's how they compare to what we just built.

### `{% include %}` with context

You can put nav HTML in a partial template and include it everywhere:

```htmldjango
{% include "nav.html" %}
```

This avoids copy-pasting the nav markup, but the permission checks and active state logic still live in the template. As the nav grows, the template grows with it. There's no central Python definition of "what's in the nav."

### Custom inclusion template tag

You can write your own template tag that builds the nav data and renders a template:

```python
@register.inclusion_tag("nav.html", takes_context=True)
def my_nav(context):
    request = context["request"]
    items = [...]
    return {"items": items}
```

This is essentially what `django-simple-nav` does under the hood — but you'd be writing the URL resolution, active state detection, and permission filtering yourself. If that's all you need for a small project, it's a reasonable approach. `django-simple-nav` provides it as a tested, reusable package.

### Context processor

A context processor can inject nav data into every template:

```python
def nav_context(request):
    return {"nav_items": [...]}
```

This makes nav data available globally, but it runs on every request — even ones that don't render a nav. It also doesn't give you a clean separation between nav structure and nav rendering.

### Other packages

The [Django Packages navigation grid](https://djangopackages.org/grids/g/navigation/) lists other options. A few worth noting:

- [**django-simple-menu**](https://github.com/jazzband/django-simple-menu) — A well-established library that takes a class-based approach similar to `django-simple-nav`, with a focus on menu hierarchies and visibility conditions. It has been around longer and has a large user base.
- [**django-navutils**](https://github.com/agateblue/django-navutils) — Provides breadcrumbs and menus with a node-based API.

Each takes a slightly different approach to the same problem. Pick the one that fits how you think about navigation in your project.
