import pytest

from identity.domain.email import Email, InvalidEmail


def test_email_normalises_case_and_whitespace():
    assert Email(" Romen@Example.COM ") == Email("romen@example.com")
    assert Email(" Romen@Example.COM ").value == "romen@example.com"


@pytest.mark.parametrize("raw", ["romen", "romen@", "@example.com", "a@b@c.com", "", "a b@c.com"])
def test_email_rejects_invalid(raw):
    with pytest.raises(InvalidEmail):
        Email(raw)


def test_email_rejects_missing_domain():
    with pytest.raises(InvalidEmail):
        Email("romen@")
