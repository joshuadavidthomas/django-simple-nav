from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings
from model_bakery import baker

from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem

pytestmark = pytest.mark.django_db


def test_get_context_data(req):
    group = NavGroup(
        title="Test",
        items=[
            NavItem(
                title="Test",
                url="/test/",
                extra_context={"foo": "bar"},
            ),
        ],
        url="/test/",
        extra_context={"baz": "qux"},
    )

    group_context = group.get_context_data(req)

    assert {"title", "url", "active", "items", "baz"} == set(group_context.keys())
    assert group_context.get("title") == "Test"
    assert group_context.get("url") == "/test/"
    assert group_context.get("active") is False
    assert group_context.get("items") is not None
    assert len(group_context.get("items")) == 1
    assert group_context.get("baz") == "qux"

    item_context = group_context.get("items")[0]

    assert {"title", "url", "active", "items", "foo"} == set(item_context.keys())
    assert item_context.get("title") == "Test"
    assert item_context.get("url") == "/test/"
    assert item_context.get("active") is False
    assert item_context.get("items") is None
    assert item_context.get("foo") == "bar"


@pytest.mark.parametrize(
    "items,expected",
    [
        (
            [
                NavItem(title=..., url="/test/"),
                NavItem(title=..., url="/test2/"),
            ],
            2,
        ),
        (
            [
                NavItem(title=..., url="/test/", permissions=["is_authenticated"]),
                NavItem(title=..., url="/test2/"),
            ],
            1,
        ),
        (
            [
                NavItem(title=..., url="/test/", permissions=["is_authenticated"]),
                NavItem(title=..., url="/test2/", permissions=["is_authenticated"]),
            ],
            0,
        ),
    ],
)
def test_get_context_data_items_anonymous(items, expected, req):
    group = NavGroup(title=..., items=items)

    req.user = AnonymousUser()

    group_context = group.get_context_data(req)

    assert len(group_context.get("items")) == expected


@pytest.mark.parametrize(
    "items,expected",
    [
        (
            [
                NavItem(title=..., url="/test/"),
                NavItem(title=..., url="/test2/"),
            ],
            2,
        ),
        (
            [
                NavItem(title=..., url="/test/", permissions=["is_authenticated"]),
                NavItem(title=..., url="/test2/"),
            ],
            2,
        ),
        (
            [
                NavItem(title=..., url="/test/", permissions=["is_authenticated"]),
                NavItem(title=..., url="/test2/", permissions=["is_authenticated"]),
            ],
            2,
        ),
    ],
)
def test_get_context_data_items_is_authenticated(items, expected, req):
    group = NavGroup(title=..., items=items)

    req.user = baker.make(get_user_model())

    group_context = group.get_context_data(req)

    assert len(group_context.get("items")) == expected


def test_get_items(req):
    group = NavGroup(
        title=...,
        items=[
            NavItem(title=..., url="/test/"),
            NavItem(title=..., url="/test2/"),
        ],
    )

    items = group.get_items(req)

    assert items[0].url == "/test/"
    assert items[1].url == "/test2/"


def test_get_items_override(req):
    class GetItemsNavGroup(NavGroup):
        def get_items(self, request):
            items = super().get_items(request)
            return [
                NavItem(title=item.title, url=f"{item.url.rstrip('/')}/overridden/")
                for item in items
            ]

    group = GetItemsNavGroup(
        title=...,
        items=[
            NavItem(title=..., url="/test/"),
            NavItem(title=..., url="/test2/"),
        ],
    )

    items = group.get_items(req)

    assert items[0].url == "/test/overridden/"
    assert items[1].url == "/test2/overridden/"


@pytest.mark.parametrize(
    "url,append_slash,expected",
    [
        (None, True, ""),
        (None, False, ""),
        ("/test", True, "/test/"),
        ("/test", False, "/test"),
        ("home", True, "/"),
        ("home", False, "/"),
    ],
)
def test_get_url(url, append_slash, expected):
    group = NavGroup(title=..., url=url, items=[...])

    with override_settings(APPEND_SLASH=append_slash):
        rendered_url = group.get_url()

        if rendered_url not in ["", "/"]:
            assert rendered_url.endswith("/") is append_slash
        assert rendered_url == expected


def test_get_url_override():
    class GetURLNavGroup(NavGroup):
        def get_url(self):
            url = super().get_url()
            if url == "":
                msg = "empty URL"
                raise ValueError(msg)
            return url

    group = GetURLNavGroup(title=..., items=[...])

    with pytest.raises(ValueError, match="empty URL"):
        group.get_url()


@pytest.mark.parametrize(
    "url,expected",
    [
        ("/test/", True),
        ("/test/active/", True),
        ("/foo/", False),
    ],
)
def test_get_active(url, expected, rf):
    group = NavGroup(
        title=...,
        url="http://testserver/test/",
        items=[
            NavItem(title=..., url="http://testserver/test/active/"),
            NavItem(title=..., url="http://testserver/test/not-active/"),
        ],
    )

    req = rf.get(url)

    assert group.get_active(req) is expected


@pytest.mark.parametrize(
    "url,items,expected",
    [
        (
            None,
            [
                NavItem(title=..., url=...),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=...),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            None,
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            None,
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
            ],
            False,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
            ],
            True,
        ),
    ],
)
def test_items_check_permissions_anonymous(url, items, expected, req):
    group = NavGroup(title=..., url=url, items=items)

    req.user = AnonymousUser()

    assert group.check_permissions(req) is expected


@pytest.mark.parametrize(
    "url,items,expected",
    [
        (
            None,
            [
                NavItem(title=..., url=...),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=...),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            None,
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=...),
            ],
            True,
        ),
        (
            None,
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
            ],
            True,
        ),
        (
            "/test/",
            [
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
                NavItem(title=..., url=..., permissions=["is_authenticated"]),
            ],
            True,
        ),
    ],
)
def test_items_check_permissions_is_authenticated(url, items, expected, req):
    group = NavGroup(title=..., url=url, items=items)

    req.user = baker.make(get_user_model())

    assert group.check_permissions(req) is expected
