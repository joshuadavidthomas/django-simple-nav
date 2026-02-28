from __future__ import annotations

from django.http import HttpRequest

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem


class DummyNav(Nav):
    template_name = "tests/dummy_nav.html"
    items = [
        NavItem(title="Relative URL", url="/relative-url"),
        NavItem(title="Absolute URL", url="https://example.com/absolute-url"),
        NavItem(title="Named URL", url="fake-view"),
        NavGroup(
            title="Group",
            url="/group",
            items=[
                NavItem(title="Relative URL", url="/relative-url"),
                NavItem(title="Absolute URL", url="https://example.com/absolute-url"),
                NavItem(title="Named URL", url="fake-view"),
            ],
        ),
        NavItem(
            title="is_authenticated Item", url="#", permissions=["is_authenticated"]
        ),
        NavItem(title="is_staff Item", url="#", permissions=["is_staff"]),
        NavItem(title="is_superuser Item", url="#", permissions=["is_superuser"]),
        NavItem(
            title="tests.dummy_perm Item", url="#", permissions=["tests.dummy_perm"]
        ),
        NavGroup(
            title="is_authenticated Group",
            permissions=["is_authenticated"],
            items=[NavItem(title="Test Item", url="#")],
        ),
        NavGroup(
            title="is_staff Group",
            permissions=["is_staff"],
            items=[NavItem(title="Test Item", url="#")],
        ),
        NavGroup(
            title="is_superuser Group",
            permissions=["is_superuser"],
            items=[NavItem(title="Test Item", url="#")],
        ),
        NavGroup(
            title="tests.dummy_perm Group",
            permissions=["tests.dummy_perm"],
            items=[NavItem(title="Test Item", url="#")],
        ),
    ]


def dynamic_nav(request: HttpRequest) -> Nav:
    """A callable nav factory for testing."""
    items = [NavItem(title="Home", url="/")]
    if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
        items.append(NavItem(title="Dashboard", url="/dashboard/"))
    return Nav(template_name="tests/dummy_nav.html", items=items)


def bad_callable(request: HttpRequest) -> str:
    """Returns something that is not a Nav (for error testing)."""
    return "not a Nav"
