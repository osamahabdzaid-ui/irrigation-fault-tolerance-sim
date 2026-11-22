# Reliability-weighted probe fusion with FAO-56 adaptive thresholds: simulation code and results

Closed-loop simulation of a zone-wise irrigation controller for Hillah, Iraq
(NASA POWER daily weather, 2020-2025). Simulation only: nothing here is an
experimental measurement.

## Contents
- `data/weather_hillah.csv` - NASA POWER daily series for 32.48 N, 44.42 E. MD5 94cc58a0b5bd232e86ef0a2c3579fe5f
- `code/irrigation_fault_tolerance_sim_v9.ipynb` - frozen simulation (v9). Protocol SHA-256 reported in the manuscript: cd557bdc216717f938a1f57d22a5c21a55dd6a9318969d0a831ab1645015ea52 (hash of the code cells before the held-out test).
- `code/irrigation_fault_tolerance_sim_v9_with_export.ipynb` - same code with export of per-run outputs.
- `code/harness.py`, `batch.py`, `confusion.py`, `figs_new.py` - re-execution harness (records per-probe flags per cycle), sensitivity batch, exact confusion counts, figures.
- `results_test/` - held-out test outputs (seeds 1000-1099): `per_seed_test.csv`, `sim_results_test_seed1000.csv`, `paired_stats_test.csv`, `detection_test.csv`, `run_config_test.json`.
- `results_sensitivity/` - configurations and results of the noise, offset, ET-error and soil sensitivity runs (development seeds 5000-5039, 6000-6019) and the large-offset runs.
- `results_v10/` - stall-watchdog variant (v10), tested on seeds 2000-2099 against criteria written beforehand. It did not meet criteria C1 and C5 and is not part of the proposed controller.

## Protocol
Development seeds 0-29; held-out test seeds 1000-1099 (years 2024-2025); code frozen before the test; deviations logged in the manuscript.

## To complete before deposit
- Choose a licence (none is set here).
- Check that the notebook hash matches the value in the manuscript with the method described there.
- Deposit on a persistent service (for example Zenodo) and put the DOI in the manuscript.
