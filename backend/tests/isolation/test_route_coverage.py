from django.urls import URLPattern, URLResolver, get_resolver

from tests.isolation.registry import ROUTES


def _route_names(patterns, prefix="") -> list[str]:
    names = []
    for p in patterns:
        if isinstance(p, URLResolver):
            names += _route_names(p.url_patterns, prefix + str(p.pattern))
        elif isinstance(p, URLPattern):
            names.append(p.name or f"<unnamed: {prefix}{p.pattern}>")
    return names


def test_every_route_is_registered():
    missing = sorted(set(_route_names(get_resolver().url_patterns)) - set(ROUTES))
    assert not missing, f"Routes missing from tests/isolation/registry.py: {missing}"


def test_registry_has_no_stale_routes():
    stale = sorted(set(ROUTES) - set(_route_names(get_resolver().url_patterns)))
    assert not stale, f"Registry entries with no route: {stale}"


def test_tenant_routes_have_a_target_factory():
    missing = [n for n, c in ROUTES.items() if c.kind == "tenant" and c.make_target is None]
    assert not missing
