from __future__ import annotations

from django import template
from django.http import HttpRequest
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context
from django.utils.module_loading import import_string

from django_simple_nav._typing import override
from django_simple_nav.nav import Nav

register = template.Library()


@register.tag(name="django_simple_nav")
def do_django_simple_nav(parser: Parser, token: Token) -> DjangoSimpleNavNode:
    tag_name, *args = token.split_contents()

    if not args:
        raise template.TemplateSyntaxError(f"{tag_name} tag requires arguments")

    nav = args[0]
    template_name = None

    if len(args) > 2:
        raise template.TemplateSyntaxError(f"{tag_name} received too many arguments")

    if len(args) == 2:
        arg = args[1]
        if "=" in arg:
            key, template_name = arg.split("=", 1)
            if key != "template_name":
                raise template.TemplateSyntaxError(
                    f"Unknown argument to {tag_name}: {key}"
                )
        else:
            template_name = arg

    return DjangoSimpleNavNode(nav, template_name)


class DjangoSimpleNavNode(template.Node):
    def __init__(self, nav: str, template_name: str | None) -> None:
        self.nav = template.Variable(nav)
        self.template_name = template.Variable(template_name) if template_name else None

    @override
    def render(self, context: Context) -> str:
        request = self.get_request(context)
        nav = self.get_nav(context, request)
        template_name = self.get_template_name(context)

        return nav.render(request, template_name)

    def get_nav(self, context: Context, request: HttpRequest) -> Nav:
        try:
            nav: str | Nav = self.nav.resolve(context)
        except template.VariableDoesNotExist as err:
            raise template.TemplateSyntaxError(
                f"Variable does not exist: {err}"
            ) from err

        if isinstance(nav, Nav):
            return nav

        if isinstance(nav, str):
            try:
                imported: object = import_string(nav)
            except ImportError as err:
                raise template.TemplateSyntaxError(
                    f"Failed to import from dotted string: {nav}"
                ) from err

            if isinstance(imported, type):
                # Class (Nav subclass or otherwise) - instantiate with no args
                nav_instance: object = imported()
            elif callable(imported):
                # Callable factory - call with request
                nav_instance = imported(request)
            else:
                nav_instance = imported
        else:
            nav_instance = nav

        if not isinstance(nav_instance, Nav):
            raise template.TemplateSyntaxError(
                f"Not a valid `Nav` instance: {nav_instance}"
            )

        return nav_instance

    def get_template_name(self, context: Context) -> str | None:
        try:
            template_name = (
                self.template_name.resolve(context) if self.template_name else None
            )
        except template.VariableDoesNotExist as err:
            raise template.TemplateSyntaxError(
                f"Variable does not exist: {err}"
            ) from err

        return template_name

    def get_request(self, context: Context) -> HttpRequest:
        request = context.get("request", None)

        if not request:
            raise template.TemplateSyntaxError(
                f"`request` not found in template context: {context}"
            )

        if not isinstance(request, HttpRequest):
            raise template.TemplateSyntaxError(
                f"`request` not a valid `HttpRequest`: {request}"
            )

        return request
