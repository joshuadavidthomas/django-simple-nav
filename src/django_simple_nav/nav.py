from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import cast
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import urlunparse

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.functional import Promise
from django.utils.safestring import mark_safe

from ._templates import get_template_engine
from ._typing import EngineTemplate
from ._typing import override

logger = logging.getLogger(__name__)


class NavItemContext(dict):
    """A dict subclass that can render itself as HTML in templates.

    Supports both dict-style access ({{ item.title }}) and self-rendering
    ({{ item }}) in Django templates.
    """

    def __init__(self, data: dict[str, object], *, rendered: str = "") -> None:
        super().__init__(data)
        self._rendered = rendered

    def __str__(self) -> str:
        return self._rendered

    def __html__(self) -> str:
        return self._rendered


def _build_renderable_context(
    item: NavGroup | NavItem, request: HttpRequest
) -> NavItemContext:
    """Build a NavItemContext for a nav item, recursively wrapping children."""
    context = item.get_context_data(request)
    child_items = item.get_items(request)
    if child_items is not None:
        context["items"] = [
            _build_renderable_context(child, request) for child in child_items
        ]
    rendered = mark_safe(
        render_to_string(item.get_template_name(), context, request)
    )
    return NavItemContext(context, rendered=rendered)


@dataclass(frozen=True)
class Nav:
    template_name: str | None = field(init=False, default=None)
    items: list[NavGroup | NavItem] | None = field(init=False, default=None)

    def render(self, request: HttpRequest, template_name: str | None = None) -> str:
        context = self.get_context_data(request)
        template = self.get_template(template_name)
        if isinstance(template, str):
            engine = get_template_engine()
            template: EngineTemplate = engine.from_string(template)  # type: ignore[no-redef]
        return template.render(context, request)

    def get_context_data(self, request: HttpRequest) -> dict[str, object]:
        items = self.get_items(request)
        return {
            "items": [_build_renderable_context(item, request) for item in items],
        }

    def get_items(self, request: HttpRequest) -> list[NavGroup | NavItem]:
        if self.items is not None:
            return [item for item in self.items if item.check_permissions(request)]

        msg = f"{self.__class__!r} must define 'items' or override 'get_items()'"
        raise ImproperlyConfigured(msg)

    def get_template(self, template_name: str | None = None) -> EngineTemplate:
        template_name = template_name or self.get_template_name()
        template = get_template(template_name=template_name)
        return cast(EngineTemplate, template)

    def get_template_name(self) -> str:
        if self.template_name is not None:
            return self.template_name

        msg = f"{self.__class__!r} must define 'template_name' or override 'get_template_name()'"
        raise ImproperlyConfigured(msg)


@dataclass(frozen=True)
class NavItem:
    title: str
    url: str | Callable[..., str] | Promise | None = None
    permissions: list[str | Callable[[HttpRequest], bool]] = field(default_factory=list)
    extra_context: dict[str, object] = field(default_factory=dict)
    append_slash: bool | None = None
    template_name: str | None = None

    def get_context_data(self, request: HttpRequest) -> dict[str, object]:
        context = {
            "title": self.get_title(),
            "url": self.get_url(),
            "active": self.get_active(request),
            "items": self.get_items(request),
        }
        # filter out any items in `extra_context` that may be shadowing the
        # above `context` dict
        extra_context = {
            key: value
            for key, value in self.extra_context.copy().items()
            if context.get(key) is None
        }
        return {
            **context,
            **extra_context,
        }

    def get_template_name(self) -> str:
        if self.template_name is not None:
            return self.template_name
        return "django_simple_nav/navitem.html"

    def render(self, request: HttpRequest) -> str:
        return str(_build_renderable_context(self, request))

    def get_title(self) -> str:
        return mark_safe(self.title)

    def get_url(self) -> str:
        url: str | None

        if isinstance(self.url, Promise):
            # django.urls.base.reverse_lazy
            url = str(self.url)
        elif callable(self.url):
            # django.urls.base.reverse (or some other basic callable)
            url = self.url()
        else:
            try:
                url = reverse(self.url)
            except NoReverseMatch:
                url = self.url

        if url is not None:
            parsed_url = urlparse(url)
            path = parsed_url.path
            should_append = (
                self.append_slash
                if self.append_slash is not None
                else settings.APPEND_SLASH
            )
            if should_append and not path.endswith("/"):
                path += "/"
            url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment,
                )
            )
            return url

        msg = f"{self.__class__!r} must define 'url' or override 'get_url()'"
        raise ImproperlyConfigured(msg)

    def get_active(self, request: HttpRequest) -> bool:
        try:
            url = self.get_url()
        except ImproperlyConfigured:
            url = None

        if not url:
            return False

        parsed_url = urlparse(url)
        parsed_request = urlparse(request.build_absolute_uri())

        if (parsed_url.scheme and (parsed_url.scheme != parsed_request.scheme)) or (
            parsed_url.netloc and (parsed_url.netloc != parsed_request.netloc)
        ):
            return False

        url_path = parsed_url.path
        request_path = parsed_request.path

        should_append = (
            self.append_slash
            if self.append_slash is not None
            else settings.APPEND_SLASH
        )
        if should_append:
            url_path = url_path.rstrip("/") + "/"
            request_path = request_path.rstrip("/") + "/"

        url_query = parse_qs(parsed_url.query)
        request_query = parse_qs(parsed_request.query)

        return url_path == request_path and url_query == request_query

    def get_items(self, request: HttpRequest) -> list[NavGroup | NavItem] | None:
        # this needs to be set to shadow the built-in `items()` of the dict
        # returned by this method for `NavItem`. otherwise when looping through
        # the items in a `Nav`, calling `{% if item.items %}` will resolve to `True`.
        # this is a consequence of getting rid of `RenderedNavItem` from earlier versions
        # of `django-simple-nav` which was done to slightly simplfy the library. though
        # given this hack, maybe that wasn't really worth it? idk... i guess it could
        # have been called `children` or `subnav`, but i started with `items` and
        # i'd rather have API consistency and this hack.
        return None

    def check_permissions(self, request: HttpRequest) -> bool:
        if not apps.is_installed("django.contrib.auth"):
            logger.warning(
                "The 'django.contrib.auth' app is not installed, so permissions will not be checked."
            )
            return True

        if not hasattr(request, "user"):
            # if no user attached to request, we assume that the user is not authenticated
            # and we should hide if *any* permissions are set
            return not self.permissions

        if not self.permissions:
            return True

        # explicitly cast to AbstractUser to make static type checkers happy
        # `django-stubs` types `request.user` as `django.contrib.auth.base_user.AbstractBaseUser`
        # as opposed to `django.contrib.auth.models.AbstractUser` or `django.contrib.auth.models.User`
        # so any type checkers will complain if this is not casted
        user = cast(AbstractUser, request.user)

        permission_checks: list[bool] = []

        for idx, perm in enumerate(self.permissions):
            has_perm = False

            if getattr(user, "is_superuser", False):
                permission_checks.append(True)
                break
            elif callable(perm):
                has_perm = perm(request)
            elif perm in ["is_authenticated", "is_staff"]:
                has_perm = getattr(user, perm, False)
            else:
                has_perm = user.has_perm(perm)

            permission_checks.append(has_perm)

            if not idx == len(self.permissions) - 1:
                continue

        return all(permission_checks)


@dataclass(frozen=True)
class NavGroup(NavItem):
    items: list[NavGroup | NavItem] = field(default_factory=list)

    @override
    def get_template_name(self) -> str:
        if self.template_name is not None:
            return self.template_name
        return "django_simple_nav/navgroup.html"

    @override
    def get_context_data(self, request: HttpRequest) -> dict[str, object]:
        context = super().get_context_data(request)

        items = self.get_items(request)
        context["items"] = [item.get_context_data(request) for item in items]

        return context

    @override
    def get_items(self, request: HttpRequest) -> list[NavGroup | NavItem]:
        return [item for item in self.items if item.check_permissions(request)]

    @override
    def get_url(self) -> str:
        try:
            url = super().get_url()
        except ImproperlyConfigured:
            return ""
        return url

    @override
    def get_active(self, request: HttpRequest) -> bool:
        if super().get_active(request):
            return True
        items = self.get_items(request)
        return any(item.get_active(request) for item in items)

    @override
    def check_permissions(self, request: HttpRequest) -> bool:
        has_perm = super().check_permissions(request)

        sub_items = [
            sub_item
            for sub_item in self.items
            if sub_item.check_permissions(request) is not False
        ]
        if not sub_items and not self.url:
            has_perm = False

        return has_perm
