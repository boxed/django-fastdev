from django.urls import (
    include,
    path,
)


def index_view(request):
    pass


def artist_view(request):
    pass


urlpatterns = [
    path('', index_view),
    path('artist/', artist_view, name='artist-view'),
    path('module/', include('tests.module.urls')),
]
