from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.template.backends.django import Template as DjangoTemplate
from django.template.backends.jinja2 import Template as JinjaTemplate
from django.test import override_settings
from model_bakery import baker

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavItem
from tests.navs import DummyNav
from tests.utils import count_anchors

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "user, expected_count",
    [
        (AnonymousUser(), 7),
        (None, 10),
    ],
)
def test_nav_render(user, expected_count, req):
    if not isinstance(user, AnonymousUser):
        user = baker.make(get_user_model())

    req.user = user

    rendered_nav = DummyNav().render(req)

    assert count_anchors(rendered_nav) == expected_count


@pytest.mark.parametrize(
    "permission, expected_count",
    [
        ("", 10),  # regular authenticated user
        ("is_staff", 13),
        ("is_superuser", 19),
        ("tests.dummy_perm", 13),
    ],
)
def test_nav_render_permissions(req, permission, expected_count):
    user = baker.make(get_user_model())

    if permission == "tests.dummy_perm":
        dummy_perm = baker.make(
            "auth.Permission",
            codename="dummy_perm",
            name="Dummy Permission",
            content_type=baker.make("contenttypes.ContentType", app_label="tests"),
        )
        user.user_permissions.add(dummy_perm)
    else:
        setattr(user, permission, True)

    user.save()
    req.user = user

    rendered_nav = DummyNav().render(req)

    assert count_anchors(rendered_nav) == expected_count


def test_nav_render_template_name(req):
    req.user = AnonymousUser()

    rendered_nav = DummyNav().render(req, "tests/alternate.html")

    assert "This is an alternate template." in rendered_nav


def test_nav_render_template_string(req):
    class StringTemplateNav(Nav):
        title = ...
        items = [
            NavItem(title=..., url="/test/"),
        ]

        def get_template(self, template_name):
            return "<h1>This is a string.</h1>"

    rendered_nav = StringTemplateNav().render(req)

    assert "<h1>This is a string.</h1>" in rendered_nav
    assert count_anchors(rendered_nav) == 0


def test_get_context_data(req):
    context = DummyNav().get_context_data(req)

    assert context["items"] is not None


def test_get_context_data_override(req):
    class OverrideNav(DummyNav):
        def get_context_data(self, request):
            return {"foo": "bar"}

    context = OverrideNav().get_context_data(req)

    assert context["foo"] == "bar"


def test_get_items(req):
    class GetItemsNav(Nav):
        template_name = ...
        items = [
            NavItem(title=..., url=...),
        ]

    items = GetItemsNav().get_items(req)

    assert len(items) == 1


def test_get_items_override(req):
    class GetItemsNav(Nav):
        template_name = ...

        def get_items(self, request):
            return [
                NavItem(title=..., url=...),
            ]

    items = GetItemsNav().get_items(req)

    assert len(items) == 1


def test_get_items_improperly_configured(req):
    class GetItemsNav(Nav):
        template_name = ...

    with pytest.raises(ImproperlyConfigured):
        GetItemsNav().get_items(req)


@pytest.mark.parametrize(
    "engine,expected",
    [
        (
            "django.template.backends.django.DjangoTemplates",
            DjangoTemplate,
        ),
        (
            "django.template.backends.jinja2.Jinja2",
            JinjaTemplate,
        ),
    ],
)
def test_get_template_engines(engine, expected):
    class TemplateEngineNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [...]

    with override_settings(
        TEMPLATES=[dict(settings.TEMPLATES[0], BACKEND=engine, DIRS=[])]
    ):
        template = TemplateEngineNav().get_template()

    assert isinstance(template, expected)


def test_get_template_override(req):
    class TemplateOverrideNav(Nav):
        items = [NavItem(title=..., url="/test/")]

        def get_template(self, *args, **kwargs):
            return "<h1>Overridden Template</h1>"

    template = TemplateOverrideNav().get_template()

    assert isinstance(template, str)

    rendered_nav = TemplateOverrideNav().render(req)

    assert "<h1>Overridden Template</h1>" in rendered_nav


def test_get_template_argument():
    class TemplateOverrideNav(Nav):
        template_name = "foo.html"
        items = [...]

    template = TemplateOverrideNav().get_template(template_name="tests/dummy_nav.html")

    assert "tests/dummy_nav.html" in str(template.origin)
    assert "foo.html" not in str(template.origin)


def test_get_template_name():
    class GetTemplateNameNav(Nav):
        template_name = "tests/dummy_nav.html"
        items = [...]

    template_name = GetTemplateNameNav().get_template_name()

    assert template_name == "tests/dummy_nav.html"


def test_get_template_name_override():
    class GetTemplateNameNav(Nav):
        items = [...]

        def get_template_name(self):
            return "tests/dummy_nav.html"

    template_name = GetTemplateNameNav().get_template_name()

    assert template_name == "tests/dummy_nav.html"


def test_get_template_name_improperly_configured():
    class GetTemplateNameNav(Nav):
        items = [...]

    with pytest.raises(ImproperlyConfigured):
        GetTemplateNameNav().get_template_name()


class TestNavConstructor:
    """Tests for direct Nav() construction (programmatic usage)."""

    def test_constructor_with_items_and_template_name(self, req):
        nav = Nav(
            template_name="tests/dummy_nav.html",
            items=[NavItem(title="Home", url="/")],
        )

        rendered = nav.render(req)

        assert "Home" in rendered
        assert count_anchors(rendered) == 1

    def test_constructor_no_args(self):
        nav = Nav()

        assert nav.template_name is None
        assert nav.items is None

    def test_constructor_items_only(self, req):
        nav = Nav(items=[NavItem(title="Test", url="/test/")])

        items = nav.get_items(req)

        assert len(items) == 1

    def test_constructor_template_name_only(self):
        nav = Nav(template_name="tests/dummy_nav.html")

        assert nav.get_template_name() == "tests/dummy_nav.html"

    def test_constructor_frozen(self):
        nav = Nav(
            template_name="tests/dummy_nav.html",
            items=[NavItem(title="Home", url="/")],
        )

        with pytest.raises(AttributeError):
            nav.template_name = "other.html"

    def test_constructor_keyword_only(self):
        with pytest.raises(TypeError):
            Nav("tests/dummy_nav.html", [])

    def test_subclass_not_shadowed(self):
        """Existing subclass pattern continues to work."""
        nav = DummyNav()

        assert nav.template_name == "tests/dummy_nav.html"
        assert nav.items is not None
        assert len(nav.items) > 0

    def test_constructor_with_conditional_items(self, req):
        items = [NavItem(title="Home", url="/")]
        items.append(NavItem(title="About", url="/about/"))

        nav = Nav(template_name="tests/dummy_nav.html", items=items)

        assert len(nav.get_items(req)) == 2
