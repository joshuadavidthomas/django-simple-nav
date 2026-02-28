from __future__ import annotations

from django.http import HttpRequest

from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavGroup
from django_simple_nav.nav import NavItem


class ExampleListNav(Nav):
    template_name = "navs/example_list.html"
    items = [
        NavItem(title="Basic", url="/basic/"),
        NavItem(title="Permissions", url="/permissions/"),
        NavItem(title="Extra Context", url="/extra-context/"),
        NavItem(title="Nested `Nav`", url="/nested/"),
        NavGroup(
            title="Frameworks",
            items=[
                NavItem(title="Tailwind CSS", url="/tailwind/"),
                NavItem(title="Bootstrap 4", url="/bootstrap4/"),
                NavItem(title="Bootstrap 5", url="/bootstrap5/"),
                NavItem(title="Pico CSS", url="/picocss/"),
            ],
        ),
    ]


class BasicNav(Nav):
    template_name = "navs/basic.html"
    items = [
        NavItem(title="Home", url="/basic/"),
        NavItem(title="Link", url="#"),
        NavGroup(
            title="Group",
            items=[
                NavItem(title="Link", url="#"),
                NavItem(title="Another link", url="#"),
            ],
        ),
        NavGroup(
            title="Group with Link",
            url="#",
            items=[
                NavItem(title="Link", url="#"),
                NavItem(title="Another link", url="#"),
            ],
        ),
    ]


def query_param_permission(request: HttpRequest) -> bool:
    return request.GET.get("permission", None) == "query_param_permission"


class PermissionsNav(Nav):
    template_name = "navs/basic.html"
    items = [
        NavItem(title="Everyone can see this link", url="#"),
        NavItem(
            title="You are not logged in",
            url="#",
            permissions=["is_anonymous"],
        ),
        NavItem(
            title="You are authenticated",
            url="#",
            permissions=["is_authenticated"],
        ),
        NavItem(
            title="You are a staff member",
            url="#",
            permissions=["is_staff"],
        ),
        NavItem(
            title="You are a superuser",
            url="#",
            permissions=["is_superuser"],
        ),
        NavItem(
            title="You have the `demo_permission`",
            url="#",
            permissions=["demo_permission"],
        ),
        NavItem(
            title="This item depends on a permission in the query params of the URL",
            url="#",
            permissions=[query_param_permission],
        ),
    ]


class SetPermissionsNav(Nav):
    template_name = "navs/basic.html"
    items = [
        NavItem(title="AnonymousUser", url="/permissions/"),
        NavItem(
            title="`is_authenticated`",
            url="/permissions/?permission=is_authenticated",
        ),
        NavItem(
            title="`is_staff`",
            url="/permissions/?permission=is_staff",
        ),
        NavItem(
            title="`is_superuser`",
            url="/permissions/?permission=is_superuser",
        ),
        NavItem(
            title="Permission `demo_permission`",
            url="/permissions/?permission=demo_permission",
        ),
        NavItem(
            title="Callable permission",
            url="/permissions/?permission=query_param_permission",
        ),
    ]


class ExtraContextNav(Nav):
    template_name = "navs/extra_context.html"
    items = [
        NavItem(title="Normal Link", url="#"),
        NavItem(title="Has Extra Context", url="#", extra_context={"foo": "bar"}),
    ]


class NestedNav(BasicNav):
    template_name = "navs/nested.html"


class TailwindMainNav(Nav):
    template_name = "navs/tailwind_main.html"
    items = [
        NavItem(title="Dashboard", url="/tailwind/"),
        NavItem(title="Team", url="#"),
        NavItem(title="Projects", url="#"),
        NavItem(title="Calendar", url="#"),
    ]


class TailwindProfileNav(Nav):
    template_name = "navs/tailwind_profile.html"
    items = [
        NavItem(title="Your Profile", url="#"),
        NavItem(title="Settings", url="#"),
        NavItem(title="Sign out", url="#"),
    ]


class Bootstrap4Nav(Nav):
    template_name = "navs/bootstrap4.html"
    items = [
        NavItem(title="Home", url="/bootstrap4/"),
        NavItem(title="Link", url="#"),
        NavItem(title="Disabled", url="#", extra_context={"disabled": True}),
        NavGroup(
            title="Dropdown",
            items=[
                NavItem(title="Action", url="#"),
                NavItem(title="Another action", url="#"),
                NavItem(title="Something else here", url="#"),
            ],
        ),
    ]


class Bootstrap5Nav(Bootstrap4Nav):
    template_name = "navs/bootstrap5.html"


class PicoCSSNav(Nav):
    template_name = "navs/picocss.html"
    items = [
        NavItem(title="Services", url="/picocss/"),
        NavGroup(
            title="Account",
            items=[
                NavItem(title="Profile", url="#"),
                NavItem(title="Settings", url="#"),
                NavItem(title="Security", url="#"),
                NavItem(title="Logout", url="#"),
            ],
        ),
    ]
