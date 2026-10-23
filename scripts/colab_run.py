"""

import os
import subprocess
import sys
from pathlib import Path
EpiScope Google Colab runner

Upload this file to Colab or copy each # %% cell into notebook cells.
The script is intentionally command-oriented: it installs dependencies and
runs the repository stages in the documented order.

Required Colab setup:
1. Upload or clone the repository into /content.
2. Set REPO_DIR below if the repository folder has a different name.
3. Keep the hash salt in Colab secrets or enter it at the prompt. Never commit it.
"""

# %% [markdown]
# # EpiScope: Google Colab execution
#
# Run the cells from top to bottom. The smoke run uses a small dataset. The
# full run is the assignment-scale run and may take a long time on Colab.

# %%
# Install the pinned project dependencies.
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r", "/content/EpiScore/requirements.txt"],
    check=True,
)

# %%
# Clone instead of uploading when the repository is public.
# !git clone https://github.com/mdrobiulhassan/EpiScore.git /content/EpiScore

# %%
import getpass

REPO_DIR = Path("/content/EpiScore")
os.chdir(REPO_DIR)

# Spark worker processes must use the same Python executable in Colab.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Keep this value outside the repository. In a real submission, use Colab
# Secrets instead of typing it directly into a notebook cell.
os.environ["EPISCOPE_HASH_SALT"] = getpass.getpass(
    "Enter EPISCOPE_HASH_SALT (not saved in the repository): "
)

print(f"Working directory: {Path.cwd()}")
print(f"Python executable: {sys.executable}")

# %%
# Optional: verify Spark and the solver before processing data.
subprocess.run([sys.executable, "scripts/check_spark.py"], check=True)
subprocess.run(
    [sys.executable, "-c", "import pyspark, pulp; print(pyspark.__version__, pulp.__version__)"],
    check=True,
)

# %%
# Smoke run: validates generator -> Bronze -> Silver -> Gold -> analytics -> serving.
# Use this before the full run. It creates only 10,000 synthetic encounters.
subprocess.run(
    [sys.executable, "scripts/run_pipeline.py", "--rows", "10000", "--seed", "42"],
    check=True,
)

# %%
# Assignment-scale run.
# The assignment requires at least 25,000,000 records at SF=1.
# This can require substantial temporary storage and several minutes.
subprocess.run(
    [
        sys.executable,
        "scripts/run_pipeline.py",
        "--rows",
        "25000000",
        "--seed",
        "42",
    ],
    check=True,
)

# %%
# Required scale experiment commands.
# Run each in a fresh output directory or archive results between runs.
for scale_rows in (6250000, 12500000, 25000000):
    subprocess.run(
        [
            sys.executable,
            "scripts/run_pipeline.py",
            "--rows",
            str(scale_rows),
            "--seed",
            "42",
        ],
        check=True,
    )

# %%
# Idempotency demonstration: run the same incremental input twice and compare
# Silver/Gold row counts. The second run must not create duplicate records.
subprocess.run(
    [sys.executable, "scripts/run_pipeline.py", "--rows", "10000", "--seed", "42"],
    check=True,
)
subprocess.run(
    [sys.executable, "scripts/run_pipeline.py", "--rows", "10000", "--seed", "42"],
    check=True,
)

# %%
# Hidden 14-day drop.
# Put the instructor's files into /content/EpiScore/data/incremental_drop first.
# The files must use the documented schema; do not rename or edit them.
# Replace this command with the repository's incremental entry point if the
# hidden-drop contract provides a dedicated folder or command.
# !python scripts/run_pipeline.py --rows 0 --incremental-dir data/incremental_drop

# %%
# Run the automated tests.
subprocess.run([sys.executable, "-m", "pytest", "-q"], check=True)

# %%
# Check serving payload sizes and suppression boundaries.
from pathlib import Path

serving_files = sorted(Path("dashboard/data").glob("*.json"))
total_bytes = sum(path.stat().st_size for path in serving_files)
print("Dashboard files:")
for path in serving_files:
    print(f"  {path}: {path.stat().st_size / 1024 / 1024:.2f} MB")
print(f"Total dashboard payload: {total_bytes / 1024 / 1024:.2f} MB")
assert total_bytes <= 10 * 1024 * 1024, "VIS-4 failed: dashboard payload exceeds 10 MB"

# %%
# Start the dashboard server. Colab will print a local URL; use a Colab
# port-forwarding helper or open the server through the notebook environment.
# !python -m http.server 8000 --directory dashboard

# %%
# Optional Colab port forwarding:
# from google.colab import output
# output.serve_kernel_port_as_window(8000)
