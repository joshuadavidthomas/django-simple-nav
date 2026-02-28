from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse
from django.urls import reverse_lazy
from model_bakery import baker

from django_simple_nav.nav import NavItem

pytestmark = pytest.mark.django_db


def test_get_context_data(req):
    item = NavItem(
        title="Test",
        url="/test/",
        permissions=["is_authenticated"],
        extra_context={"foo": "bar"},
    )

    context = item.get_context_data(req)

    assert {"title", "url", "active", "items", "foo"} == set(context.keys())
    assert context.get("title") == "Test"
    assert context.get("url") == "/test/"
    assert context.get("active") is False
    assert context.get("items") is None
    assert context.get("foo") == "bar"


def test_get_context_data_no_extra_context(req):
    item = NavItem(
        title="Test",
        url="/test/",
    )

    rendered_item = item.get_context_data(req)

    assert rendered_item.get("foo") is None


def test_get_context_data_extra_context_shadowing(req):
    item = NavItem(
        title="Test",
        url="/test/",
        extra_context={"title": "Shadowed"},
    )

    rendered_item = item.get_context_data(req)

    assert rendered_item.get("title") == "Test"


def test_get_title():
    item = NavItem(title="Test")

    assert item.get_title() == "Test"


def test_get_title_safestring():
    item = NavItem(title="Test!!!")

    assert item.get_title() == "Test!!!"


def test_get_title_override():
    class GetTitleNavItem(NavItem):
        def get_title(self):
            return f"{self.title}!!!"

    item = GetTitleNavItem(title="Test")

    assert item.get_title() == "Test!!!"


@pytest.mark.parametrize(
    "url,append_slash,expected",
    [
        ("/test", True, "/test/"),
        ("/test", False, "/test"),
        ("home", True, "/"),
        ("home", False, "/"),
        (reverse("home"), True, "/"),
        (reverse("home"), False, "/"),
        (reverse_lazy("home"), True, "/"),
        (reverse_lazy("home"), False, "/"),
    ],
)
def test_get_url(url, append_slash, expected):
    item = NavItem(title=..., url=url)

    with override_settings(APPEND_SLASH=append_slash):
        rendered_url = item.get_url()

        if rendered_url != "/":
            assert rendered_url.endswith("/") is append_slash
        assert rendered_url == expected


@pytest.mark.parametrize(
    "url,append_slash_setting,append_slash_item,expected",
    [
        # append_slash=None falls back to settings.APPEND_SLASH
        ("/test", True, None, "/test/"),
        ("/test", False, None, "/test"),
        # append_slash=False ignores settings.APPEND_SLASH
        ("/test", True, False, "/test"),
        ("/test", False, False, "/test"),
        # append_slash=True always appends
        ("/test", True, True, "/test/"),
        ("/test", False, True, "/test/"),
    ],
)
def test_get_url_append_slash(url, append_slash_setting, append_slash_item, expected):
    item = NavItem(title=..., url=url, append_slash=append_slash_item)

    with override_settings(APPEND_SLASH=append_slash_setting):
        assert item.get_url() == expected


@pytest.mark.parametrize(
    "append_slash_item,expected",
    [
        (None, True),
        (False, True),
        (True, True),
    ],
)
def test_active_append_slash_item(append_slash_item, expected, rf):
    item = NavItem(
        title=..., url="http://testserver/test", append_slash=append_slash_item
    )

    req = rf.get("/test")

    with override_settings(APPEND_SLASH=True):
        assert item.get_active(req) is expected


def test_get_url_improperly_configured():
    item = NavItem(title=..., url=None)

    with pytest.raises(ImproperlyConfigured):
        item.get_url()


def test_get_url_override():
    class GetURLNavItem(NavItem):
        def get_url(self):
            return "/"

    item = GetURLNavItem(title=..., url=None)

    assert item.get_url() == "/"


@pytest.mark.parametrize(
    "url,req_path,req_params,expected",
    [
        ("/test/", "/test/", None, True),
        ("/test/", "/other/", None, False),
        ("fake-view", "/fake-view/", None, True),
        ("/test", "/test/", None, True),
        ("/test/", "/test", None, True),
        ("/test/nested/", "/test/", None, False),
        ("/test/?query=param", "/test/", {"query": "param"}, True),
        ("/test/?query=param", "/test/", None, False),
    ],
)
def test_active(url, req_path, req_params, expected, rf):
    item = NavItem(title=..., url=f"http://testserver/{url.lstrip('/')}")

    req = rf.get(req_path, req_params)

    assert item.get_active(req) == expected


def test_active_different_scheme(rf):
    item = NavItem(title=..., url="https://testserver/")

    req = rf.get("/")

    assert item.get_active(req) is False


def test_active_different_domain(rf):
    item = NavItem(title=..., url="http://different-domain/")

    req = rf.get("/")

    assert item.get_active(req) is False


def test_active_no_scheme_no_netloc(rf):
    item = NavItem(title=..., url="/test/")

    req = rf.get("/test")

    assert item.get_active(req) is True


@pytest.mark.parametrize("append_slash", [True, False])
def test_active_append_slash_setting(append_slash, rf):
    item = NavItem(title=..., url="http://testserver/test")

    req = rf.get("/test")

    with override_settings(APPEND_SLASH=append_slash):
        assert item.get_active(req) is True


def test_active_improperly_configured(req):
    item = NavItem(title=..., url=None)

    req.path = "/"

    assert item.get_active(req) is False


def test_active_reverse_no_match(req):
    item = NavItem(title=..., url="nonexistent")

    req.path = "/"

    assert item.get_active(req) is False


def test_get_items(req):
    item = NavItem(title=..., url=...)

    assert item.get_items(req) is None


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], True),
        (["is_authenticated"], False),
        (["is_active"], False),
        (["is_staff"], False),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], False),
        (["is_authenticated", "is_superuser"], False),
        (["is_anonymous", "is_authenticated"], False),
    ],
)
def test_check_permissions_anonymous(permissions, expected, req):
    item = NavItem(title=..., url=..., permissions=permissions)

    req.user = AnonymousUser()

    assert item.check_permissions(req) is expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], False),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], False),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], False),
        (["is_authenticated", "is_superuser"], False),
    ],
)
def test_check_permissions_is_authenticated(permissions, expected, req):
    item = NavItem(title=..., url=..., permissions=permissions)

    req.user = baker.make(get_user_model())

    assert item.check_permissions(req) is expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], False),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], True),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], True),
        (["is_authenticated", "is_superuser"], False),
    ],
)
def test_check_permissions_is_staff(permissions, expected, req):
    item = NavItem(title=..., url=..., permissions=permissions)

    req.user = baker.make(get_user_model(), is_staff=True)

    assert item.check_permissions(req) is expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], True),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], True),
        (["is_superuser"], True),
        (["is_authenticated", "is_staff"], True),
        (["is_authenticated", "is_superuser"], True),
    ],
)
def test_check_permissions_is_superuser(permissions, expected, req):
    item = NavItem(title=..., url=..., permissions=permissions)

    req.user = baker.make(get_user_model(), is_superuser=True)

    assert item.check_permissions(req) is expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], False),
        (["is_authenticated"], False),
        (["is_active"], False),
        (["is_staff"], False),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], False),
        (["is_authenticated", "is_superuser"], False),
    ],
)
def test_check_permissions_no_request_user(permissions, expected, req):
    item = NavItem(title=..., url=..., permissions=permissions)

    assert item.check_permissions(req) is expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], True),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], True),
        (["is_superuser"], True),
        (["is_authenticated", "is_staff"], True),
        (["is_authenticated", "is_superuser"], True),
    ],
)
@override_settings(
    INSTALLED_APPS=[
        app for app in settings.INSTALLED_APPS if app != "django.contrib.auth"
    ]
)
def test_check_permissions_no_contrib_auth(permissions, expected, req, caplog):
    item = NavItem(title=..., url=..., permissions=permissions)

    with caplog.at_level("WARNING"):
        assert item.check_permissions(req) is expected

    assert "The 'django.contrib.auth' app is not installed" in caplog.text


def test_check_permissions_callable_anonymous(req):
    def dummy_check(request):
        return True

    item = NavItem(title=..., url=..., permissions=[dummy_check])

    req.user = AnonymousUser()

    assert item.check_permissions(req)


@pytest.mark.parametrize("is_authenticated", [True, False])
def test_check_permissions_callable_is_authenticated(is_authenticated, req):
    def check_is_authenticated(request):
        return request.user.is_authenticated

    item = NavItem(title=..., url=..., permissions=[check_is_authenticated])

    req.user = baker.make(get_user_model()) if is_authenticated else AnonymousUser()

    assert item.check_permissions(req) is is_authenticated


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], False),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], False),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], False),
        (["is_authenticated", "is_superuser"], False),
    ],
)
def test_check_permissions_auth_permission_is_authenticated(permissions, expected, req):
    dummy_perm = baker.make(
        "auth.Permission",
        codename="dummy_perm",
        name="Dummy Permission",
        content_type=baker.make("contenttypes.ContentType", app_label="tests"),
    )

    item = NavItem(
        title=...,
        url=...,
        permissions=permissions
        + [f"{dummy_perm.content_type.app_label}.{dummy_perm.codename}"],
    )

    user = baker.make(get_user_model())
    user.user_permissions.add(dummy_perm)
    req.user = user

    assert item.check_permissions(req) == expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], False),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], True),
        (["is_superuser"], False),
        (["is_authenticated", "is_staff"], True),
        (["is_authenticated", "is_superuser"], False),
    ],
)
def test_check_permissions_auth_permission_is_staff(permissions, expected, req):
    dummy_perm = baker.make(
        "auth.Permission",
        codename="dummy_perm",
        name="Dummy Permission",
        content_type=baker.make("contenttypes.ContentType", app_label="tests"),
    )

    item = NavItem(
        title=...,
        url=...,
        permissions=permissions
        + [f"{dummy_perm.content_type.app_label}.{dummy_perm.codename}"],
    )

    user = baker.make(get_user_model(), is_staff=True)
    user.user_permissions.add(dummy_perm)
    req.user = user

    assert item.check_permissions(req) == expected


@pytest.mark.parametrize(
    "permissions,expected",
    [
        ([], True),
        (["is_anonymous"], True),
        (["is_authenticated"], True),
        (["is_active"], True),
        (["is_staff"], True),
        (["is_superuser"], True),
        (["is_authenticated", "is_staff"], True),
        (["is_authenticated", "is_superuser"], True),
    ],
)
def test_check_permissions_auth_permission_is_superuser(permissions, expected, req):
    dummy_perm = baker.make(
        "auth.Permission",
        codename="dummy_perm",
        name="Dummy Permission",
        content_type=baker.make("contenttypes.ContentType", app_label="tests"),
    )

    item = NavItem(
        title=...,
        url=...,
        permissions=permissions
        + [f"{dummy_perm.content_type.app_label}.{dummy_perm.codename}"],
    )

    user = baker.make(get_user_model(), is_superuser=True)
    user.user_permissions.add(dummy_perm)
    req.user = user

    assert item.check_permissions(req) == expected
