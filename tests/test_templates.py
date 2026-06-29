from __future__ import annotations

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from django_simple_nav._templates import get_template_engine


def test_get_template_engine():
    engine = get_template_engine()

    assert engine.name in settings.TEMPLATES[0].get("BACKEND")


@override_settings(TEMPLATES=[])
def test_get_template_engine_no_engine():
    with pytest.raises(ImproperlyConfigured):
        get_template_engine()


@override_settings(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
        },
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
        },
    ]
)
@pytest.mark.parametrize(
    "templates,expected",
    [
        (
            [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                },
                {
                    "BACKEND": "django.template.backends.jinja2.Jinja2",
                },
            ],
            "django",
        ),
        (
            [
                {
                    "BACKEND": "django.template.backends.jinja2.Jinja2",
                },
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                },
            ],
            "jinja2",
        ),
    ],
)
def test_get_template_engine_multiple(templates, expected, caplog):
    with override_settings(TEMPLATES=templates), caplog.at_level("WARNING"):
        engine = get_template_engine()

    assert engine.name == expected
    assert "Multiple `BACKEND` defined for a template engine." in caplog.text


@pytest.mark.parametrize(
    "using,expected",
    [
        ("django", "django"),
        ("django2", "django2"),
        ("jinja2", "jinja2"),
    ],
)
@override_settings(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
        },
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "NAME": "django2",
        },
        {
            "BACKEND": "django.template.backends.jinja2.Jinja2",
        },
    ]
)
def test_get_template_engine_using(using, expected):
    engine = get_template_engine(using)

    assert engine.name == expected


@pytest.mark.parametrize(
    "app_setting,expected",
    [
        ("django.template.backends.django.DjangoTemplates", "django"),
        ("django.template.backends.jinja2.Jinja2", "jinja2"),
    ],
)
def test_get_template_engine_app_setting(app_setting, expected):
    with override_settings(
        DJANGO_SIMPLE_NAV={"TEMPLATE_BACKEND": app_setting},
        TEMPLATES=[
            {
                "BACKEND": app_setting,
            },
        ],
    ):
        engine = get_template_engine()

    assert engine.name == expected


@override_settings(
    DJANGO_SIMPLE_NAV={"TEMPLATE_BACKEND": "invalid"},
)
def test_get_template_engine_app_setting_invalid():
    with pytest.raises(ImproperlyConfigured) as exc_info:
        get_template_engine()

    assert "Invalid `TEMPLATE_BACKEND` for a template engine" in str(exc_info.value)
