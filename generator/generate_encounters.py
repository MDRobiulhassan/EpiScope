
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "bronze" / "encounters"
FACILITY_OUTPUT = ROOT / "data" / "bronze" / "facilities.csv"
GROUND_TRUTH_OUTPUT = ROOT / "data" / "bronze" / "ground_truth_outbreaks.csv"

DISTRICTS = [
    "Bagerhat", "Bandarban", "Barguna", "Barishal", "Bhola",
    "Bogura", "Brahmanbaria", "Chandpur", "Chapainawabganj",
    "Chattogram", "Chuadanga", "Cox's Bazar", "Cumilla", "Dhaka",
    "Dinajpur", "Faridpur", "Feni", "Gaibandha", "Gazipur",
    "Gopalganj", "Habiganj", "Jamalpur", "Jashore", "Jhalokati",
    "Jhenaidah", "Joypurhat", "Khagrachhari", "Khulna",
    "Kishoreganj", "Kurigram", "Kushtia", "Lakshmipur",
    "Lalmonirhat", "Madaripur", "Magura", "Manikganj", "Meherpur",
    "Moulvibazar", "Munshiganj", "Mymensingh", "Naogaon", "Narail",
    "Narayanganj", "Narsingdi", "Natore", "Netrokona", "Nilphamari",
    "Noakhali", "Pabna", "Panchagarh", "Patuakhali", "Pirojpur",
    "Rajbari", "Rajshahi", "Rangamati", "Rangpur", "Satkhira",
    "Shariatpur", "Sherpur", "Sirajganj", "Sunamganj", "Sylhet",
    "Tangail", "Thakurgaon",
]

DISEASES = [
    "Dengue",
    "Diarrhoea",
    "Malaria",
    "Respiratory Infection",
    "Typhoid",
]
SEVERITIES = ["mild", "moderate", "severe"]
ICD10_CODES = {
    "Dengue": "A90",
    "Diarrhoea": "A09",
    "Malaria": "B50",
    "Respiratory Infection": "J11",
    "Typhoid": "A01",
}

START_DATE = date(2021, 1, 1)
END_DATE = date(2025, 12, 31)
DATE_COUNT = (END_DATE - START_DATE).days + 1


def random_date(rng):
    return START_DATE + timedelta(days=rng.randrange(DATE_COUNT))


def make_outbreaks(rng, count=30):
    """Create outbreak windows and a set for fast ground-truth lookup."""
    windows = []

    for _ in range(count):
        district = rng.choice(DISTRICTS)
        disease = rng.choice(DISEASES)
        start = START_DATE + timedelta(
            days=rng.randrange(DATE_COUNT - 21)
        )
        end = start + timedelta(days=rng.randint(7, 14))
        windows.append((district, disease, start, end))

    active_keys = set()

    for district, disease, start, end in windows:
        current = start
        while current <= end:
            active_keys.add((district, disease, current))
            current += timedelta(days=1)

    return windows, active_keys


def generate_record(encounter_id, rng, windows, active_keys):
    # Most records use ordinary background sampling. A small fraction
    # are deliberately concentrated in outbreak windows, creating spikes.
    if rng.random() < 0.005:
        district, disease, start, end = rng.choice(windows)
        encounter_date = start + timedelta(
            days=rng.randrange((end - start).days + 1)
        )
    else:
        district = rng.choice(DISTRICTS)
        disease = rng.choice(DISEASES)
        encounter_date = random_date(rng)

    is_outbreak = (
        district, disease, encounter_date
    ) in active_keys

    # A simple synthetic seasonal pattern for dengue.
    if disease == "Dengue" and encounter_date.month in (7, 8, 9, 10):
        severity_weights = [58, 30, 12]
    else:
        severity_weights = [65, 27, 8]

    if is_outbreak:
        severity_weights = [35, 40, 25]

    age = rng.randint(0, 100)
    temperature = round(rng.uniform(35.0, 40.5), 1)
    rainfall = round(rng.uniform(0.0, 300.0), 1)

    # Deliberately inject invalid data to test Silver validation.
    if rng.random() < 0.005:
        age = 150
    if rng.random() < 0.002:
        temperature = 99.9

    delay_days = min(21, int(rng.expovariate(1 / 3.5)))
    report_date = encounter_date + timedelta(days=delay_days)
    severity = rng.choices(SEVERITIES, weights=severity_weights, k=1)[0]
    admitted = severity == "severe" or rng.random() < 0.08
    patient_id = f"PAT-{rng.randrange(1, max(100, int(0.72 * 25000000))):09d}"

    return {
        "encounter_id": encounter_id,
        "patient_id": patient_id,
        "facility_id": f"FAC-{rng.randrange(1, 601):04d}",
        "onset_date": encounter_date.isoformat(),
        "report_date": report_date.isoformat(),
        "encounter_date": encounter_date.isoformat(),
        "district": district,
        "disease": disease,
        "icd10_code": ICD10_CODES[disease],
        "age": age,
        "sex": rng.choice(["F", "M", "X"]),
        "severity": severity,
        "temperature_c": temperature,
        "rainfall_mm": rainfall,
        "lab_confirmed": rng.random() < (0.65 if disease != "Respiratory Infection" else 0.35),
        "admitted": admitted,
        "outcome": "recovered" if rng.random() < 0.985 else "deceased",
        "synthetic_outbreak": is_outbreak,
        "source": "synthetic",
    }


def write_facility_registry():
    FACILITY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with FACILITY_OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["facility_id", "district", "facility_type", "beds", "icu_beds"],
        )
        writer.writeheader()
        for facility_number in range(1, 601):
            district = DISTRICTS[(facility_number - 1) % len(DISTRICTS)]
            beds = 20 + (facility_number * 17) % 181
            writer.writerow(
                {
                    "facility_id": f"FAC-{facility_number:04d}",
                    "district": district,
                    "facility_type": ["hospital", "clinic", "upazila_health_complex"][facility_number % 3],
                    "beds": beds,
                    "icu_beds": max(1, beds // 12),
                }
            )


def write_ground_truth(windows):
    GROUND_TRUTH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with GROUND_TRUTH_OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["district", "disease", "start_date", "end_date", "outbreak_type"],
        )
        writer.writeheader()
        for index, (district, disease, start, end) in enumerate(windows):
            writer.writerow(
                {
                    "district": district,
                    "disease": disease,
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "outbreak_type": "slow_growth" if index == 0 else "seasonal_spike",
                }
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--scale-factor", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--chunk-size", type=int, default=100000)
    args = parser.parse_args()

    if args.rows <= 0 or args.scale_factor <= 0 or args.chunk_size <= 0:
        parser.error("rows, scale-factor, and chunk-size must be positive")

    total_rows = int(args.rows * args.scale_factor)
    rng = random.Random(args.seed)
    windows, active_keys = make_outbreaks(rng)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "encounters.csv"

    fields = [
        "encounter_id",
        "patient_id",
        "facility_id",
        "onset_date",
        "report_date",
        "encounter_date",
        "district",
        "disease",
        "icd10_code",
        "age",
        "sex",
        "severity",
        "temperature_c",
        "rainfall_mm",
        "lab_confirmed",
        "admitted",
        "outcome",
        "synthetic_outbreak",
        "source",
    ]

    write_facility_registry()
    write_ground_truth(windows)

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for start_id in range(1, total_rows + 1, args.chunk_size):
            end_id = min(start_id + args.chunk_size, total_rows + 1)

            for encounter_id in range(start_id, end_id):
                generated_id = (
                    rng.randint(1, encounter_id - 1)
                    if encounter_id > 1 and rng.random() < 0.02
                    else encounter_id
                )
                writer.writerow(
                    generate_record(
                        generated_id, rng, windows, active_keys
                    )
                )

            print(f"Generated {end_id - 1:,} / {total_rows:,}")

    print(f"Districts: {len(DISTRICTS)}")
    print(f"Rows: {total_rows:,}")
    print(f"CSV: {output_file}")
    print(f"Facilities: {FACILITY_OUTPUT}")
    print(f"Ground truth: {GROUND_TRUTH_OUTPUT}")


if __name__ == "__main__":
    main()
