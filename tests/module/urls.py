from django.urls import path


def index_view(request):
    pass


def artist_view(request):
    pass


app_name = 'module'

urlpatterns = [
    path('', index_view),
    path('artist/', artist_view, name='artist-view2'),
]
