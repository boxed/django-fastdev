import pytest
from django.shortcuts import render

from django_fastdev.apps import FastDevVariableDoesNotExist, check_for_migrations_in_gitignore, check_for_pycache_vscode_cache_in_gitignore, check_for_venv_in_gitignore, validate_fk_field
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


def test_if_does_not_fire_exception():
    render(req('get'), template_name='test_if_does_not_fire_exception.html')


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


def test_if_gitignore_has_migrations():
    line = 'migrations/'
    errors = check_for_migrations_in_gitignore(line)
    errors_expected = True
    assert errors == errors_expected


def test_if_gitignore_doesnt_have_migrations():
    line = 'not_migrations/'
    errors = check_for_migrations_in_gitignore(line)
    assert errors == None

def test_if_venv_is_ignored():
    line= 'venv/'
    errors = check_for_venv_in_gitignore('venv',line)
    assert errors == True

def test_if_venv_is_not_ignored():
    line= ''
    errors = check_for_venv_in_gitignore('venv',line)
    assert errors == None


def test_if_pycache_vscode_cache_is_ignored():
    line = 'pycache/'
    errors = check_for_pycache_vscode_cache_in_gitignore(line)
    assert errors == True

    line = 'vscode/'
    errors = check_for_pycache_vscode_cache_in_gitignore(line)
    assert errors == True

def test_if_pycache_vscode_cache_is_not_ignored():
    line = ''
    errors = check_for_pycache_vscode_cache_in_gitignore(line)
    assert errors == None

    line = ''
    errors = check_for_pycache_vscode_cache_in_gitignore(line)
    assert errors == None


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
