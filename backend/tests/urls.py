from django.urls import include, path

from config.urls import urlpatterns as app_urlpatterns

urlpatterns = [
    *app_urlpatterns,
    path("api/test/", include("tests.fixtures.sample_notes.api.urls")),
]
