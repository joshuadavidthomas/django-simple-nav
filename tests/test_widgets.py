from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem
from django_simple_nav.nav import NavItemContext

pytestmark = pytest.mark.django_db


# NavItemContext


def test_navitemcontext_dict_access():
    ctx = NavItemContext(
        {"title": "Home", "url": "/", "active": True},
        rendered="<a href='/'>Home</a>",
    )
    assert ctx["title"] == "Home"
    assert ctx["url"] == "/"
    assert ctx["active"] is True


def test_navitemcontext_str_renders_html():
    ctx = NavItemContext(
        {"title": "Home"},
        rendered="<a href='/'>Home</a>",
    )
    assert str(ctx) == "<a href='/'>Home</a>"


def test_navitemcontext_html_method():
    ctx = NavItemContext(
        {"title": "Home"},
        rendered="<a href='/'>Home</a>",
    )
    assert ctx.__html__() == "<a href='/'>Home</a>"


def test_navitemcontext_default_rendered():
    ctx = NavItemContext({"title": "Home"})
    assert str(ctx) == ""


# NavItem.get_template_name


def test_navitem_get_template_name_default():
    item = NavItem(title="Test", url="/test/")
    assert item.get_template_name() == "django_simple_nav/navitem.html"


def test_navitem_get_template_name_custom():
    item = NavItem(title="Test", url="/test/", template_name="custom/item.html")
    assert item.get_template_name() == "custom/item.html"


def test_navitem_get_template_name_override():
    class CustomNavItem(NavItem):
        def get_template_name(self):
            return "custom/item.html"

    item = CustomNavItem(title="Test", url="/test/")
    assert item.get_template_name() == "custom/item.html"


# NavGroup.get_template_name


def test_navgroup_get_template_name_default():
    group = NavGroup(title="Test", items=[])
    assert group.get_template_name() == "django_simple_nav/navgroup.html"


def test_navgroup_get_template_name_custom():
    group = NavGroup(title="Test", items=[], template_name="custom/group.html")
    assert group.get_template_name() == "custom/group.html"


# NavItem.render


def test_navitem_render(req):
    item = NavItem(title="Home", url="/")
    rendered = item.render(req)
    assert "<a" in rendered
    assert 'href="/"' in rendered
    assert "Home" in rendered


def test_navitem_render_active(rf):
    item = NavItem(title="Home", url="http://testserver/")
    req = rf.get("/")
    rendered = item.render(req)
    assert 'aria-current="page"' in rendered


def test_navitem_render_no_url(req):
    item = NavItem(title="Label")

    with pytest.raises(ImproperlyConfigured):
        item.render(req)


def test_navitem_render_returns_str(req):
    item = NavItem(title="Home", url="/")
    rendered = item.render(req)
    assert isinstance(rendered, str)


# NavGroup.render


def test_navgroup_render(req):
    group = NavGroup(
        title="About",
        url="/about/",
        items=[
            NavItem(title="Team", url="/team/"),
            NavItem(title="Jobs", url="/jobs/"),
        ],
    )
    rendered = group.render(req)
    assert "About" in rendered
    assert "Team" in rendered
    assert "Jobs" in rendered


def test_navgroup_render_children_as_html(req):
    group = NavGroup(
        title="About",
        url="/about/",
        items=[
            NavItem(title="Team", url="/team/"),
        ],
    )
    rendered = group.render(req)
    assert "<ul>" in rendered
    assert "<li>" in rendered


def test_navgroup_render_no_url(req):
    group = NavGroup(
        title="About",
        items=[
            NavItem(title="Team", url="/team/"),
        ],
    )
    rendered = group.render(req)
    assert "<span>" in rendered
    assert "About" in rendered


# Nav.get_context_data returns NavItemContext


def test_nav_get_context_data_returns_navitemcontext(req):
    class TestNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [
            NavItem(title="Home", url="/"),
        ]

    context = TestNav().get_context_data(req)
    items = context["items"]
    assert len(items) == 1
    assert isinstance(items[0], NavItemContext)


def test_nav_get_context_data_navitemcontext_has_dict_keys(req):
    class TestNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [
            NavItem(title="Home", url="/"),
        ]

    context = TestNav().get_context_data(req)
    item = context["items"][0]
    assert item["title"] == "Home"
    assert item["url"] == "/"
    assert "active" in item


def test_nav_get_context_data_navitemcontext_renders(req):
    class TestNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [
            NavItem(title="Home", url="/"),
        ]

    context = TestNav().get_context_data(req)
    item = context["items"][0]
    rendered = str(item)
    assert "<a" in rendered
    assert "Home" in rendered


def test_nav_get_context_data_navgroup_children_are_navitemcontext(req):
    class TestNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [
            NavGroup(
                title="About",
                items=[
                    NavItem(title="Team", url="/team/"),
                    NavItem(title="Jobs", url="/jobs/"),
                ],
            ),
        ]

    req.user = AnonymousUser()
    context = TestNav().get_context_data(req)
    group = context["items"][0]
    assert isinstance(group, NavItemContext)
    children = group["items"]
    assert len(children) == 2
    assert isinstance(children[0], NavItemContext)
    assert isinstance(children[1], NavItemContext)
    assert children[0]["title"] == "Team"


# Template rendering with {{ item }}


def test_nav_render_with_self_rendering_items(req):
    """Test that {{ item }} in a template produces rendered HTML."""

    class SelfRenderNav(Nav):
        template_name = "tests/self_render_nav.html"
        items = [
            NavItem(title="Home", url="/"),
            NavItem(title="About", url="/about/"),
        ]

    rendered = SelfRenderNav().render(req)
    assert "<a" in rendered
    assert "Home" in rendered
    assert "About" in rendered


def test_nav_render_with_self_rendering_group(req):
    """Test that {{ item }} renders a NavGroup with its children."""

    class SelfRenderNav(Nav):
        template_name = "tests/self_render_nav.html"
        items = [
            NavGroup(
                title="About",
                url="/about/",
                items=[
                    NavItem(title="Team", url="/team/"),
                ],
            ),
        ]

    rendered = SelfRenderNav().render(req)
    assert "About" in rendered
    assert "Team" in rendered


# Backward compatibility


def test_backward_compat_dict_access_in_template(req):
    """Existing templates using {{ item.title }} still work."""
    from tests.navs import DummyNav
    from tests.utils import count_anchors

    req.user = AnonymousUser()
    rendered = DummyNav().render(req)
    assert count_anchors(rendered) == 7


# Custom template_name per item


def test_navitem_custom_template(req):
    item = NavItem(
        title="Custom",
        url="/custom/",
        template_name="tests/custom_navitem.html",
    )
    rendered = item.render(req)
    assert "custom-item" in rendered
    assert "Custom" in rendered
