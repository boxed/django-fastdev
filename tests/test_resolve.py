import pytest
from django.shortcuts import render
from django.template import VariableDoesNotExist

from tests import req


def test_fall_through():
    assert render(req('GET'), template_name='test_resolve_fall_through.html', context=dict(a=dict(b=3))).content == b'3\n'


def test_resolve_simple():
    with pytest.raises(VariableDoesNotExist) as e:
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

    with pytest.raises(VariableDoesNotExist) as e:
        render(req('GET'), template_name='test_resolve_nested.html', context=dict(foo=Foo()))

    assert str(e.value) == '''Tried looking up foo.bar.does_not_exist in context

tests.test_resolve.Bar does not have a member does_not_exist

Available attributes:

    a
    b

The object was: <repr of Bar>
'''


def test_resolve_dict():
    with pytest.raises(VariableDoesNotExist) as e:
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
