from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jinja2 import TemplateRuntimeError
from model_bakery import baker

from django_simple_nav.nav import NavItem
from tests.jinja2.environment import environment
from tests.navs import DummyNav
from tests.utils import count_anchors

pytestmark = pytest.mark.django_db


def test_django_simple_nav_templatetag(req):
    template = environment.from_string('{{ django_simple_nav("tests.navs.DummyNav") }}')
    req.user = AnonymousUser()
    rendered_template = template.render(request=req)
    assert count_anchors(rendered_template) == 7


def test_templatetag_with_template_name(req):
    template = environment.from_string(
        "{{ django_simple_nav('tests.navs.DummyNav', 'tests/alternate.html') }}"
    )
    req.user = AnonymousUser()
    rendered_template = template.render({"request": req})
    assert "This is an alternate template." in rendered_template


def test_templatetag_with_nav_instance(req):
    class PlainviewNav(DummyNav):
        items = [
            NavItem(title="I drink your milkshake!", url="/milkshake/"),
        ]

    template = environment.from_string("{{ django_simple_nav(new_nav) }}")
    req.user = baker.make(get_user_model(), first_name="Daniel", last_name="Plainview")
    rendered_template = template.render({"request": req, "new_nav": PlainviewNav()})
    assert "I drink your milkshake!" in rendered_template


def test_templatetag_with_nav_instance_and_template_name(req):
    class DeadParrotNav(DummyNav):
        items = [
            NavItem(title="He's pinin' for the fjords!", url="/notlob/"),
        ]

    template = environment.from_string(
        "{{ django_simple_nav(new_nav, 'tests/alternate.html') }}"
    )
    req.user = baker.make(get_user_model(), first_name="Norwegian", last_name="Blue")
    rendered_template = template.render({"request": req, "new_nav": DeadParrotNav()})
    assert "He's pinin' for the fjords!" in rendered_template
    assert "This is an alternate template." in rendered_template


def test_templatetag_with_template_name_on_nav_instance(req):
    class PinkmanNav(DummyNav):
        template_name = "tests/alternate.html"
        items = [
            NavItem(title="Yeah Mr. White! Yeah science!", url="/science/"),
        ]

    template = environment.from_string("{{ django_simple_nav(new_nav) }}")
    req.user = baker.make(get_user_model(), first_name="Jesse", last_name="Pinkman")
    rendered_template = template.render({"request": req, "new_nav": PinkmanNav()})
    assert "Yeah Mr. White! Yeah science!" in rendered_template
    assert "This is an alternate template." in rendered_template


def test_templatetag_with_no_arguments(req):
    req.user = AnonymousUser()
    with pytest.raises(TypeError):
        template = environment.from_string("{{ django_simple_nav() }}")
        template.render({"request": req})


def test_templatetag_with_missing_variable(req):
    req.user = AnonymousUser()
    template = environment.from_string("{{ django_simple_nav(missing_nav) }}")
    with pytest.raises(TemplateRuntimeError):
        template.render({"request": req})


def test_nested_templatetag(req):
    # called twice to simulate a nested call
    template = environment.from_string(
        "{{ django_simple_nav('tests.navs.DummyNav') }}"
        "{{ django_simple_nav('tests.navs.DummyNav') }}"
    )
    req.user = AnonymousUser()
    rendered_template = template.render({"request": req})
    assert count_anchors(rendered_template) == 14


def test_invalid_dotted_string(req):
    template = environment.from_string(
        "{{ django_simple_nav('path.to.DoesNotExist') }}"
    )

    with pytest.raises(TemplateRuntimeError):
        template.render({"request": req})


class InvalidNav: ...


def test_invalid_nav_instance(req):
    template = environment.from_string(
        "{{ django_simple_nav('tests.test_templatetags.InvalidNav') }}"
    )
    with pytest.raises(TemplateRuntimeError):
        template.render({"request": req})


def test_template_name_variable_does_not_exist(req):
    template = environment.from_string(
        "{{ django_simple_nav('tests.navs.DummyNav', nonexistent_template_name_variable) }}"
    )
    with pytest.raises(TemplateRuntimeError):
        template.render({"request": req})


def test_request_not_in_context():
    template = environment.from_string(
        " {{ django_simple_nav('tests.navs.DummyNav') }}"
    )

    with pytest.raises(TemplateRuntimeError):
        template.render()


def test_invalid_request():
    class InvalidRequest: ...

    template = environment.from_string("{{ django_simple_nav('tests.navs.DummyNav') }}")

    with pytest.raises(TemplateRuntimeError):
        template.render({"request": InvalidRequest()})


def test_callable_dotted_string(req):
    template = environment.from_string(
        '{{ django_simple_nav("tests.navs.dynamic_nav") }}'
    )
    req.user = AnonymousUser()
    rendered_template = template.render({"request": req})

    assert "Home" in rendered_template
    assert "Dashboard" not in rendered_template


def test_callable_authenticated(req):
    template = environment.from_string(
        '{{ django_simple_nav("tests.navs.dynamic_nav") }}'
    )
    req.user = baker.make(get_user_model())
    rendered_template = template.render({"request": req})

    assert "Home" in rendered_template
    assert "Dashboard" in rendered_template


def test_callable_with_template_name(req):
    template = environment.from_string(
        "{{ django_simple_nav('tests.navs.dynamic_nav', 'tests/alternate.html') }}"
    )
    req.user = AnonymousUser()
    rendered_template = template.render({"request": req})

    assert "This is an alternate template." in rendered_template


def test_callable_variable(req):
    from tests.navs import dynamic_nav

    template = environment.from_string("{{ django_simple_nav(nav_func) }}")
    req.user = AnonymousUser()
    rendered_template = template.render({"request": req, "nav_func": dynamic_nav})

    assert "Home" in rendered_template


def test_bad_callable(req):
    template = environment.from_string(
        '{{ django_simple_nav("tests.navs.bad_callable") }}'
    )
    req.user = AnonymousUser()

    with pytest.raises(TemplateRuntimeError):
        template.render({"request": req})
