import math

import pytest

from faststats import summarize


def test_summarize_values() -> None:
    result = summarize([10, 20, 30])

    assert result.count == 3
    assert result.sum == pytest.approx(60.0)
    assert result.mean == pytest.approx(20.0)
    assert result.minimum == pytest.approx(10.0)
    assert result.maximum == pytest.approx(30.0)


def test_accepts_generator() -> None:
    result = summarize(value for value in [2, 4, 6])

    assert result.mean == pytest.approx(4.0)


def test_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        summarize([])


def test_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match=r"values\[1\]"):
        summarize([10.0, math.nan])
