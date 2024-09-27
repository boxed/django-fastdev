from django_fastdev.apps import is_absolute_url


def test_is_static_url_true():
    assert is_absolute_url('/')
    assert is_absolute_url('http://example.com')
    assert is_absolute_url('https://example.com')

def test_is_static_url_false():
    assert not is_absolute_url('example.com')
    assert not is_absolute_url('example.com/')
    assert not is_absolute_url('.')
    assert not is_absolute_url('./')
