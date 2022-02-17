import pytest
from django.forms import (
    CharField,
    Form,
)

from django_fastdev.django_app import InvalidCleanMethod


def test_ok_form_works(settings):
    settings.DEBUG = True

    class MyForm(Form):
        field = CharField()

        def clean_field(self):
            pass

    MyForm()


def test_field_clean_validation(settings):
    class MyForm(Form):
        field = CharField()

        def clean_flield(self):
            pass

    MyForm()

    settings.DEBUG = True
    with pytest.raises(InvalidCleanMethod) as e:
        MyForm()

    assert str(e.value) == """Clean method clean_flield won't apply to any field. Available fields:\n\n    field"""
