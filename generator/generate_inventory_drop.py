"""Generate one synthetic daily facility stock and bed snapshot.

This models the assignment's incremental S6 source. It is separate from the
encounter generator and never overwrites the batch encounter CSV.
"""

import argparse
import csv
import random
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FACILITY_PATH = ROOT / "data" / "bronze" / "facilities.csv"
DEFAULT_OUTPUT = ROOT / "data" / "incremental_drop" / "inventory_snapshot.csv"
sys.path.insert(0, str(ROOT))
from generator.generate_encounters import write_facility_registry

FIELDS = [
    "snapshot_date",
    "facility_id",
    "district",
    "total_beds",
    "occupied_beds",
    "iv_saline_units",
    "ns1_test_kits",
    "ors_sachets",
    "antimalarial_courses",
    "source",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-date", default="2025-12-31")
    parser.add_argument("--seed", type=int, default=999)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        snapshot_date = date.fromisoformat(args.snapshot_date)
    except ValueError as exc:
        parser.error(f"--snapshot-date must be YYYY-MM-DD: {exc}")

    if not FACILITY_PATH.exists():
        print("Facility registry is missing; creating the synthetic registry.")
        write_facility_registry()

    rng = random.Random(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with FACILITY_PATH.open(newline="", encoding="utf-8") as source:
        facilities = list(csv.DictReader(source))

    with args.output.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        for facility in facilities:
            total_beds = int(facility["beds"])
            writer.writerow(
                {
                    "snapshot_date": snapshot_date.isoformat(),
                    "facility_id": facility["facility_id"],
                    "district": facility["district"],
                    "total_beds": total_beds,
                    "occupied_beds": rng.randint(0, total_beds),
                    "iv_saline_units": rng.randint(0, 2000),
                    "ns1_test_kits": rng.randint(0, 500),
                    "ors_sachets": rng.randint(0, 5000),
                    "antimalarial_courses": rng.randint(0, 500),
                    "source": "synthetic_incremental",
                }
            )

    print(f"Snapshot date: {snapshot_date.isoformat()}")
    print(f"Facilities: {len(facilities):,}")
    print(f"Seed: {args.seed}")
    print(f"CSV: {args.output}")


if __name__ == "__main__":
    main()
