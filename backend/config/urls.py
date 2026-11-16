from django.urls import URLPattern, URLResolver, path
from drf_spectacular.views import SpectacularAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]
