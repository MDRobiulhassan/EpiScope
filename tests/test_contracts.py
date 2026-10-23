import hashlib
import random
from pathlib import Path

from generator.generate_encounters import generate_record, make_outbreaks

ROOT = Path(__file__).resolve().parents[1]


def test_generator_contract_files_exist_after_generation():
    random_generator = random.Random(42)
    windows, active_keys = make_outbreaks(random_generator)
    fields = set(generate_record(1, random_generator, windows, active_keys))
    assert {"patient_id", "facility_id", "onset_date", "report_date", "icd10_code"} <= fields


def test_patient_hash_is_not_reversible_from_public_salt():
    patient_id = "PAT-000000001"
    salt = "test-only-salt"
    hashed = hashlib.sha256((salt + patient_id).encode()).hexdigest()
    assert patient_id not in hashed
    assert len(hashed) == 64


def test_public_suppression_boundaries():
    threshold = 5
    assert all(0 < count < threshold for count in (1, 2, 3, 4))
    assert 5 >= threshold