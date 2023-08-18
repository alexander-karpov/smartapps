import sys
from typing import Tuple
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from enrichment import add_random_adjective


@patch("random.choice", return_value="красивый")
def test_add_random_adjective(mock: MagicMock):
    """
    Прилагательные должны склоняться в тот же род, что и существительные
    """
    actual = asyncio.run(add_random_adjective("лошадь", case="nomn", num="sing"))

    assert actual == "красивая лошадь"
