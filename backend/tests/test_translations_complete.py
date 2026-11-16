from pathlib import Path

import polib
import pytest
from django.utils.translation import override

import identity.api.messages  # noqa: F401  (registers identity's messages)
from shared_kernel.api.errors import MESSAGES

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"


@pytest.mark.parametrize("language", ["es", "en"])
def test_every_msgid_translated_in_es_and_en(language):
    catalog = polib.pofile(str(LOCALE_DIR / language / "LC_MESSAGES" / "django.po"))
    untranslated = [e.msgid for e in catalog if not e.msgstr or "fuzzy" in e.flags]
    assert not untranslated, f"{language}: {untranslated}"


def test_every_error_message_is_in_the_catalog():
    catalog = polib.pofile(str(LOCALE_DIR / "es" / "LC_MESSAGES" / "django.po"))
    msgids = {e.msgid for e in catalog}
    with override("en"):
        missing = [str(m) for m in MESSAGES.values() if str(m) not in msgids]
    assert not missing
