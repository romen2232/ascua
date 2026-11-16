import pytest

from shared_kernel.domain.basis_points import BasisPoints
from shared_kernel.domain.errors import InvalidValue
from shared_kernel.domain.money import Money


def test_basis_points_bounds():
    with pytest.raises(InvalidValue):
        BasisPoints(10001)
    with pytest.raises(InvalidValue):
        BasisPoints(-1)


def test_basis_points_of_rounds_half_even():
    assert BasisPoints(5000).of(Money(5)) == Money(2)
    assert BasisPoints(5000).of(Money(7)) == Money(4)


def test_basis_points_of_keeps_currency():
    assert BasisPoints(2500).of(Money(400, "USD")) == Money(100, "USD")


@pytest.mark.parametrize(("text", "value"), [("12.5", 1250), ("100", 10000), ("0", 0), ("0.01", 1)])
def test_from_percent_str(text, value):
    assert BasisPoints.from_percent_str(text) == BasisPoints(value)


@pytest.mark.parametrize("text", ["12.505", "abc", "101", "-1"])
def test_from_percent_str_rejects_invalid(text):
    with pytest.raises(InvalidValue):
        BasisPoints.from_percent_str(text)
