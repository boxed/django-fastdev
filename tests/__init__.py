from django.test import RequestFactory


def req(method, **data):
    return getattr(RequestFactory(HTTP_REFERER='/'), method.lower())('/', data=data)
