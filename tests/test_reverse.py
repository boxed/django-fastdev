import pytest
from django.urls import reverse

from django_fastdev.django_app import (
    FastDevNoReverseMatch,
    FastDevNoReverseMatchNamespace,
)


def test_reverse_no_namespace(settings):
    reverse('artist-view')

    with pytest.raises(FastDevNoReverseMatchNamespace) as e:
        reverse('doesnotexist:blabla')

    assert str(e.value) == "'doesnotexist' is not a registered namespace"

    settings.DEBUG = True
    with pytest.raises(FastDevNoReverseMatchNamespace) as e:
        reverse('doesnotexist:blabla')

    assert str(e.value) == "'doesnotexist' is not a registered namespace\n\nAvailable namespaces:\n    module"


def test_reverse_no_hit(settings):
    reverse('artist-view')

    with pytest.raises(FastDevNoReverseMatch) as e:
        reverse('doesnotexist')

    assert str(e.value) == "Reverse for 'doesnotexist' not found. 'doesnotexist' is not a valid view function or pattern name."

    settings.DEBUG = True
    with pytest.raises(FastDevNoReverseMatch) as e:
        reverse('doesnotexist')

    assert str(e.value) == "Reverse for 'doesnotexist' not found. 'doesnotexist' is not a valid view function or pattern name.\n\nThese names exist:\n\n    artist-view"

    with pytest.raises(FastDevNoReverseMatch) as e:
        reverse('module:doesnotexist')

    print(repr(e.value))
    assert str(e.value) == "Reverse for 'doesnotexist' not found. 'doesnotexist' is not a valid view function or pattern name.\n\nThese names exist:\n\n    artist-view2"
