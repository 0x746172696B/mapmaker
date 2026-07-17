import pytest
from apps.contracts.hex_color import HexColor


def test_invalid_hex_raises_valueerror():
    with pytest.raises(ValueError):
        HexColor("#8181811")


def test_valid_hex_is_normalized_to_uppercase():
    assert HexColor("#ff00aa").value == "#FF00AA"
