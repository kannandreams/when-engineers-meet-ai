"""Python-friendly wrappers around the native Rust extension."""

from collections.abc import Iterable

from ._core import Summary
from ._core import summarize as _summarize


def summarize(values: Iterable[float]) -> Summary:
    """Calculate count, sum, mean, minimum, and maximum.

    The public Python layer accepts any iterable of numeric values. It
    normalises the input before passing one batch to the Rust extension.
    """

    normalized_values = [float(value) for value in values]
    return _summarize(normalized_values)
