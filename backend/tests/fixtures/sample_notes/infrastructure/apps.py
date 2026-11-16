from django.apps import AppConfig


class SampleNotesConfig(AppConfig):
    """Test-only tenant context used to prove isolation before real contexts exist."""

    name = "tests.fixtures.sample_notes.infrastructure"
    label = "sample_notes"
