import os
from django.conf import settings
import pytest
from django.shortcuts import render
from django.core.checks import Error

from django_fastdev.apps import FastDevVariableDoesNotExist, check_for_migrations_in_gitignore
from tests import req
from django.core.checks import Error


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

def test_if_gitignore_has_migrations():
    lines = ['migrations/']
    errors = check_for_migrations_in_gitignore(lines)
    errors_expected = Error("""
        You have excluded migrations folders from git

        This is not a good idea! It's very important to commit all your migrations files into git for migrations to work properly. 

        https://docs.djangoproject.com/en/dev/topics/migrations/#version-control for more information

        Bad pattern on lines : 1""",
                hint = "You should never gitignore migrations.",)
    assert errors == errors_expected

def test_if_gitignore_doesnt_have_migrations():
    lines = ['not_migrations/']
    errors = check_for_migrations_in_gitignore(lines)
    assert errors == None
