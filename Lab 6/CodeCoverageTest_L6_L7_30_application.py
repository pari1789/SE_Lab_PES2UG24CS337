import pytest
from vending_machine import select_item, make_change, purchase


def test_invalid_item():
    assert select_item("water", {}, 100) == "invalid"


def test_sold_out_item():
    assert select_item("cola", {"cola": 0}, 200) == "sold_out"


def test_insufficient_credit():
    assert select_item("cola", {"cola": 2}, 100) == "insufficient"


def test_valid_item():
    assert select_item("cola", {"cola": 2}, 150) == "ok"


def test_negative_change():
    with pytest.raises(ValueError):
        make_change(-1)


def test_no_change_needed():
    assert make_change(0) == []


def test_exact_change():
    assert make_change(185) == [100, 50, 25, 10]


def test_no_exact_change():
    assert make_change(1) is None


def test_purchase_invalid_item():
    assert purchase("water", {}, 200) == ("invalid", [])


def test_purchase_sold_out():
    assert purchase("cola", {"cola": 0}, 200) == ("sold_out", [])


def test_purchase_insufficient_credit():
    assert purchase("cola", {"cola": 2}, 100) == ("insufficient", [])


def test_purchase_no_exact_change():
    assert purchase("cola", {"cola": 2}, 151) == ("no_exact_change", [])


def test_successful_purchase():
    stock = {"cola": 2}
    result = purchase("cola", stock, 150)
    assert result == ("dispensed", [])
    assert stock["cola"] == 1
