import sys
from typing import Tuple
import pytest


def test_inflect(cases: Tuple[str, str, str]):
    inflect

    entity = parser.find(text).fact
    nomn = entity.inflect({"nomn"})
    accs = entity.inflect({"accs"})

    assert str(nomn) == nomn_expected
    assert str(accs) == accs_expected


if __name__ == "__main__":
    sys.exit(pytest.main())
