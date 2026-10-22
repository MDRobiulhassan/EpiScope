# -*- coding: utf-8 -*-
"""
EpiScope Pipeline Orchestrator

Runs all ingestion, validation, aggregation, analytics, and serving steps
in correct dependency order, verifying outputs at each step.
"""

import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    ("Encounter Generation", [sys.executable, "generator/generate_encounters.py", "--rows", "10000"]),
    ("Bronze Ingestion", [sys.executable, "pipeline/bronze.py"]),
    ("Silver Validation", [sys.executable, "pipeline/silver.py"]),
    ("Gold Aggregation", [sys.executable, "pipeline/gold.py"]),
    ("Outbreak Detection", [sys.executable, "analytics/detection/detect_outbreaks.py"]),
    ("Outbreak Evaluation", [sys.executable, "analytics/detection/evaluate_detection.py"]),
    ("Case Forecasting", [sys.executable, "analytics/forecast/forecast_cases.py"]),
    ("Forecast Evaluation", [sys.executable, "analytics/forecast/evaluate_forecasts.py"]),
    ("Resource Allocation", [sys.executable, "analytics/optimise/allocate_resources.py"]),
    ("Preparedness Calendar", [sys.executable, "analytics/calendar/preparedness_calendar.py"]),
    ("Build Public Data", [sys.executable, "serving/build_public_data.py"]),
    ("Export Dashboard Data", [sys.executable, "serving/export_dashboard_data.py"]),
]

def run_stage(name, command):
    print(f"\n==================================================")
    print(f" RUNNING STAGE: {name}")
    print(f"==================================================")
    start = time.perf_counter()
    
    res = subprocess.run(command, cwd=str(PROJECT_ROOT), text=True)
    
    elapsed = time.perf_counter() - start
    print(f"\nSTAGE {name} completed in {elapsed:.2f} seconds with exit code: {res.returncode}")
    if res.returncode != 0:
        print(f"ERROR: Stage {name} failed!")
        sys.exit(res.returncode)

def main():
    print("Starting complete EpiScope workflow pipeline...")
    total_start = time.perf_counter()
    
    for name, command in STAGES:
        run_stage(name, command)
        
    total_elapsed = time.perf_counter() - total_start
    print(f"\n==================================================")
    print(f" PIPELINE COMPLETED SUCCESSFULLY in {total_elapsed/60:.2f} minutes")
    print(f"==================================================")

if __name__ == '__main__':
    main()
