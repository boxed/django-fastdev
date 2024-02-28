import pytest
from django.shortcuts import render
from django.template import Context
from django.views.debug import DEBUG_ENGINE

from django_fastdev.apps import (
    FastDevVariableDoesNotExist,
    strict_if,
    validate_fk_field,
)
from tests import req
from django.core.checks import Error

from tests.models import ModelWithInvalidFK_ID2, ModelWithInvalidFK_iD3, ModelWithInvalidFK_id1, ModelWithInvalidFKID4, ModelWithInvalidFKId5, ModelWithInvalidFKiD6, ModelWithValidFK


def test_fall_through():
    assert render(req('GET'), template_name='test_resolve_fall_through.html', context=dict(a=dict(b=3))).content == b'3\n'


def test_resolve_simple():
    with pytest.raises(FastDevVariableDoesNotExist) as e:
        render(req('GET'), template_name='test_resolve_simple.html')

    assert str(e.value) == '''does_not_exist does not exist in context. Available top level variables:

    False
    None
    True
    csrf_token
'''


def test_resolve_nested():

    class Bar:
        def __init__(self):
            self.a = 1
            self.b = 2

        def __repr__(self):
            return '<repr of Bar>'

    class Foo:
        def __init__(self):
            self.bar = Bar()

    with pytest.raises(FastDevVariableDoesNotExist) as e:
        render(req('GET'), template_name='test_resolve_nested.html', context=dict(foo=Foo()))

    assert str(e.value) == '''Tried looking up foo.bar.does_not_exist in context

tests.test_resolve.Bar does not have a member does_not_exist

Available attributes:

    a
    b

The object was: <repr of Bar>
'''


def test_resolve_dict():
    with pytest.raises(FastDevVariableDoesNotExist) as e:
        render(req('GET'), template_name='test_resolve_dict.html', context=dict(a=dict(b=dict(c=2))))

    assert str(e.value) == '''Tried looking up a.b.does_not_exist in context

dict does not have a key 'does_not_exist', and does not have a member does_not_exist

You can access keys in the dict by their name. Available keys:

    c

Available attributes:

    clear
    copy
    fromkeys
    get
    items
    keys
    pop
    popitem
    setdefault
    update
    values

The object was: {'c': 2}
'''


def test_if_does_not_fire_exception(settings):
    assert not strict_if()
    with pytest.warns(DeprecationWarning) as w:
        render(req('get'), template_name='test_if_does_not_fire_exception.html')

    warning, = w.list
    assert str(warning.message) == 'set FASTDEV_STRICT_IF in settings, and use {% ifexists %} instead of {% if %} to check if a variable exists.'


def test_if_fires_exception_with_strict_if(settings):
    settings.FASTDEV_STRICT_IF = True
    with pytest.raises(FastDevVariableDoesNotExist):
        render(req('get'), template_name='test_if_does_not_fire_exception.html')
    settings.FASTDEV_STRICT_IF = False


def test_ifexists_does_not_fire_exception():
    assert 'ifexists a' in render(req('get'), template_name='test_ifexists.html', context={'a': None}).content.decode()
    assert 'ifexists b' in render(req('get'), template_name='test_ifexists.html', context={'b': None}).content.decode()
    assert 'ifexists c' in render(req('get'), template_name='test_ifexists.html', context={'c': None}).content.decode()
    assert 'else' in render(req('get'), template_name='test_ifexists.html').content.decode()


def test_firstof_does_not_fire_exception():
    render(req('get'), template_name='test_firstof_does_not_fire_exception.html')


def test_crash_inside_if():
    with pytest.raises(FastDevVariableDoesNotExist) as e:
        render(req('GET'), template_name='test_crash_inside_if.html')

    assert str(e.value) == '''does_not_exist does not exist in context. Available top level variables:

    False
    None
    True
    csrf_token
'''


def test_if_fk_is_not_valid():
    expected_error = [
        'base_model_id',
        'base_model_ID',
        'base_model_iD',
        'base_modelID',
        'base_modelId',
        'base_modeliD']

    error_with_invalid_id = validate_fk_field(ModelWithInvalidFK_id1)[0]
    assert error_with_invalid_id in expected_error

    error_with_invalid_ID = validate_fk_field(ModelWithInvalidFK_ID2)[0]
    assert error_with_invalid_ID in expected_error

    error_with_invalid_iD = validate_fk_field(ModelWithInvalidFK_iD3)[0]
    assert error_with_invalid_iD in expected_error

    error_with_invalidID = validate_fk_field(ModelWithInvalidFKID4)[0]
    assert error_with_invalidID in expected_error

    error_with_invalidId = validate_fk_field(ModelWithInvalidFKId5)[0]
    assert error_with_invalidId in expected_error

    error_with_invalidiD = validate_fk_field(ModelWithInvalidFKiD6)[0]
    assert error_with_invalidiD in expected_error


def test_if_fk_is_valid():
    errors = validate_fk_field(ModelWithValidFK)
    assert not errors


def test_debug_engine(settings):
    settings.FASTDEV_STRICT_IF = True
    t = DEBUG_ENGINE.from_string('{% if does_not_exist %}{% endif %}{{ also_does_not_exist')
    t.render(Context())
