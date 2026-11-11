import re

def parse_coins(coins_csv):
    """Return a list of positive ints; invalid or empty items are skipped."""
    if not isinstance(coins_csv, str):
        return []
    coins = []
    for c in coins_csv.split(','):
        try:
            value = int(c.strip())
        except ValueError:
            continue
        if value > 0:
            coins.append(value)
    return coins

def slot_position(code):
    """Return (row, column) for codes like 'B7', or None if invalid."""
    if not isinstance(code, str):
        return None
    code = code.strip()
    if not re.fullmatch(r'[A-Za-z][0-9]+', code):
        return None
    try:
        column = int(code[1:]) - 1
    except ValueError:
        return None
    if column < 0:
        return None
    row = ord(code[0].upper()) - ord('A')
    return row, column

def change_due(payment):
    """Return e.g. '10 five-coins' for 'paid/price', or None if invalid."""
    if not isinstance(payment, str):
        return None
    parts = payment.split('/')
    if len(parts) != 2:
        return None
    try:
        paid = int(parts[0].strip())
        price = int(parts[1].strip())
    except ValueError:
        return None
    if paid < 0 or price < 0 or paid < price:
        return None
    
    return str((paid - price) // 5) + ' five-coins'

def main():
    print("==== Running parse_coins ====")
    user_input = input("Enter coin values as CSV (e.g. 5,10,25): ")
    print("Coins:", parse_coins(user_input))

    print("\n==== Running slot_position ====")
    user_input = input("Enter a slot code (e.g. B7): ")
    result = slot_position(user_input)
    print("Row and Column:", result if result is not None else "Invalid slot code")

    print("\n==== Running change_due ====")
    user_input = input("Enter paid/price (e.g. 200/150): ")
    result = change_due(user_input)
    print("Change Due:", result if result is not None else "Invalid payment")

if __name__ == "__main__":
    main()