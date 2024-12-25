import pytest
from django.forms import (
    CharField,
    Form,
)

from django_fastdev.apps import InvalidCleanMethod


def test_ok_form_works(settings):
    settings.DEBUG = True

    class MyForm(Form):
        field = CharField()

        def clean_field(self):
            pass

    MyForm()


# noinspection PyStatementEffect
def test_field_clean_validation(settings):
    class MyForm(Form):
        field = CharField()

        def clean_flield(self):
            pass

    MyForm().errors

    settings.DEBUG = True
    # set strict mode otherwise test will fail (because dynamically type form; doesn't exist in module)
    settings.FASTDEV_STRICT_FORM_CHECKING = True
    with pytest.raises(InvalidCleanMethod) as e:
        MyForm().errors

    assert str(e.value) == """Clean method clean_flield of class MyForm won't apply to any field. Available fields:\n\n    field"""


# noinspection PyStatementEffect
def test_field_clean_validation2(settings):
    class MyFormBase(Form):
        pass

    class MyForm(MyFormBase):
        def __init__(self):
            super(MyForm, self).__init__()
            self.fields['field'] = CharField()

        def clean_field(self):
            pass

        def clean_flield(self):
            pass

    MyForm().errors

    settings.DEBUG = True
    # set strict mode otherwise test will fail (because dynamically type form; doesn't exist in module)
    settings.FASTDEV_STRICT_FORM_CHECKING = True
    with pytest.raises(InvalidCleanMethod) as e:
        MyForm().errors

    assert str(e.value) == """Clean method clean_flield of class MyForm won't apply to any field. Available fields:\n\n    field"""
