from hypothesis import given, strategies as st
from vending_machine import parse_coins, slot_position, change_due

@given(st.text() | st.none())
def test_parse_coins_no_crash(s):
    try:
        parse_coins(s)
    except Exception as e:
        assert False, f"parse_coins crashed with: {e!r}"

@given(st.text() | st.none())
def test_slot_position_no_crash(s):
    try:
        slot_position(s)
    except Exception as e:
        assert False, f"slot_position crashed with: {e!r}"

@given(st.text() | st.none())
def test_change_due_no_crash(s):
    try:
        change_due(s)
    except Exception as e:
        assert False, f"change_due crashed with: {e!r}"