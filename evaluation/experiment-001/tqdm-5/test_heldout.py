"""Evaluator-only behavioral checks for tqdm 5."""

from io import StringIO

from tqdm import tqdm


def test_disabled_sized_iterable_retains_total():
    progress = tqdm(["a", "b", "c"], disable=True, file=StringIO())
    try:
        assert progress.total == 3
        assert len(progress) == 3
    finally:
        progress.close()
