from __future__ import annotations

from collections.abc import Callable

from django.utils.module_loading import import_string
from jinja2 import TemplateRuntimeError
from jinja2 import pass_context
from jinja2.runtime import Context

from django_simple_nav.nav import Nav


@pass_context
def django_simple_nav(
    context: Context,
    nav: str | Nav | Callable[..., Nav],
    template_name: str | None = None,
) -> str:
    """Jinja binding for `django_simple_nav`"""
    if (loader := context.environment.loader) is None:
        raise TemplateRuntimeError("No template loader in Jinja2 environment")

    request = context.get("request")
    if request is None:
        raise TemplateRuntimeError("`request` not found in Jinja2 context")

    nav_instance: object
    if isinstance(nav, Nav):
        nav_instance = nav
    elif isinstance(nav, str):
        try:
            resolved: object = import_string(nav)
        except ImportError as err:
            raise TemplateRuntimeError(str(err)) from err

        if isinstance(resolved, type):
            nav_instance = resolved()
        elif callable(resolved):
            nav_instance = resolved(request)
        else:
            nav_instance = resolved
    elif callable(nav):
        nav_instance = nav(request)
    else:
        nav_instance = nav

    if not isinstance(nav_instance, Nav):
        raise TemplateRuntimeError(f"Not a valid `Nav` instance: {nav_instance}")

    try:
        if template_name is None:
            template_name = nav_instance.template_name
        if template_name is None:
            raise TemplateRuntimeError("Navigation object has no template")
        new_context = {
            "request": request,
            **nav_instance.get_context_data(request),
        }
    except TemplateRuntimeError:
        raise
    except Exception as err:
        raise TemplateRuntimeError(str(err)) from err

    return loader.load(context.environment, template_name).render(new_context)
