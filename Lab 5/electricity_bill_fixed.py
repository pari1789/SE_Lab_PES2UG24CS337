"""Calculate electricity bills from meter readings and save them as JSON."""

import json
import os
import re
import subprocess

from defusedxml import ElementTree as ET


SLABS = [(100, 3.5), (200, 5.0), (300, 6.5)]
HIGH_RATE = 8.0
FIXED_CHARGE = 75
METER_XML = (
    "<meters>"
    "<meter id='M1' prev='1200' curr='1350'/>"
    "<meter id='M2' prev='5000' curr='5420'/>"
    "<meter id='M3' prev='800' curr='760'/>"
    "</meters>"
)
CLERK_PASSWORD = os.getenv("CLERK_PASSWORD", "")
bills = []


def read_meters(xml_text):
    """Parse XML meter readings into (meter_id, previous, current) tuples."""
    root = ET.fromstring(xml_text)
    return [
        (meter.get("id"), int(meter.get("prev")), int(meter.get("curr")))
        for meter in root.findall("meter")
    ]


def calculate_units(previous, current):
    """Return consumption units, treating decreasing readings as invalid."""
    if current < previous:
        print("Warning: meter reading went backwards")
        return 0
    return current - previous


def energy_charge(units):
    """Calculate the energy charge using progressive consumption slabs."""
    charge = 0
    lower = 0
    remaining = units

    for limit, rate in SLABS:
        slab_units = min(remaining, limit - lower)
        if slab_units > 0:
            charge += slab_units * rate
            remaining -= slab_units
        lower = limit

    return charge + remaining * HIGH_RATE


def generate_bill(meter_id, units, tax_rate=0.05, extras=None):
    """Generate a bill and append it to the in-memory bill list."""
    if extras is None:
        extras = {}

    amount = energy_charge(units) + FIXED_CHARGE + sum(extras.values())
    bill = {
        "meter": meter_id,
        "units": units,
        "amount": round(amount * (1 + tax_rate), 2),
    }
    bills.append(bill)
    return bill


def average_bill():
    """Return the average bill amount, or zero when there are no bills."""
    if not bills:
        return 0
    return round(sum(bill["amount"] for bill in bills) / len(bills), 2)


def save_bills(file_name="bills.json"):
    """Write generated bills to a UTF-8 JSON file."""
    with open(file_name, "w", encoding="utf-8") as output_file:
        json.dump(bills, output_file, indent=2)


def sync_meter(meter_ip):
    """Fetch a meter reading from a validated IP address or hostname."""
    if not isinstance(meter_ip, str) or not meter_ip:
        raise ValueError("Meter IP or hostname is required")

    # Accept IPv4/IPv6 literals or ordinary DNS hostnames; reject URL syntax.
    if any(char in meter_ip for char in "/\\\\@?#:"):
        raise ValueError("Provide only an IP address or hostname, not a URL")
    hostname_pattern = re.compile(
        r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}"
        r"[A-Za-z0-9])?)(?:\\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}"
        r"[A-Za-z0-9])?))*$"
    )
    if not hostname_pattern.fullmatch(meter_ip):
        raise ValueError("Invalid meter IP or hostname")

    url = f"http://{meter_ip}/reading"
    subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--", url],
        check=True,
        shell=False,
        timeout=10,
    )


def main():
    """Calculate sample bills, print a summary, and save the results."""
    for meter_id, previous, current in read_meters(METER_XML):
        units = calculate_units(previous, current)
        generate_bill(meter_id, units)

    generate_bill("M4", 50, extras={"late_fee": 25})

    for bill in bills:
        print(
            bill["meter"],
            "used",
            bill["units"],
            "units, bill Rs.",
            bill["amount"],
        )

    highest = max(bills, key=lambda bill: bill["amount"])
    print("Highest bill:", highest["meter"])
    print("Average bill:", average_bill())
    total = sum(bill["amount"] for bill in bills)
    print("Total billed:", round(total, 2))
    save_bills()
    print("Saved", len(bills), "bills to bills.json")


if __name__ == "__main__":
    main()
