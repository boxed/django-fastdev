import pytest
from django.contrib.auth.models import User
from django.db.models import Q


@pytest.mark.django_db
def test_queryset_get_error_single():
    with pytest.raises(User.DoesNotExist) as e:
        User.objects.get(username__contains='a')

    assert str(e.value) == """User matching query does not exist.

Query kwargs:

    username__contains: 'a'"""


@pytest.mark.django_db
def test_queryset_get_error_single_args():
    with pytest.raises(User.DoesNotExist) as e:
        User.objects.get(Q(username__contains='a'))

    assert str(e.value) == """User matching query does not exist.

Query args:

    (<Q: (AND: ('username__contains', 'a'))>,)"""



@pytest.mark.django_db
def test_queryset_get_error_multi():
    User.objects.create(username='aa')
    User.objects.create(username='ab')
    with pytest.raises(User.MultipleObjectsReturned) as e:
        User.objects.get(username__contains='a')

    assert str(e.value) == """get() returned more than one User -- it returned 2!

Query kwargs:

    username__contains: 'a'"""
