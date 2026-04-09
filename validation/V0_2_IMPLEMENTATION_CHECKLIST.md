# Uberbrain v0.2 Implementation Checklist

This is the executable blueprint for turning the validation spec into runnable tooling.

## 1) Deliverables (must exist)

- [x] `validation/config_v0_2.yaml`
- [x] `sim/benchmarks/run_matrix.py`
- [x] `sim/benchmarks/metrics.py`
- [x] `sim/benchmarks/baselines.py`
- [x] `sim/benchmarks/adversarial.py`
- [x] `sim/benchmarks/io.py`
- [x] `sim/models/quartz_optics.py`
- [x] `tests/test_benchmark_harness.py`
- [x] `tests/test_pass_fail_contract.py`
- [ ] `results/<run_id>/config.json`      ← generated at runtime
- [ ] `results/<run_id>/metrics.csv`      ← generated at runtime
- [ ] `results/<run_id>/summary.json`     ← generated at runtime

---

## 2) How to run

```bash
# Full benchmark
python sim/benchmarks/run_matrix.py --config validation/config_v0_2.yaml

# Smoke test (fast, for CI)
python sim/benchmarks/run_matrix.py --config validation/config_v0_2.yaml --smoke

# Single claim
python sim/benchmarks/run_matrix.py --config validation/config_v0_2.yaml --claim c1

# Run tests
pytest tests/ -v -s
```

---

## 3) Definition of done (v0.2)

v0.2 is complete when:
- [x] All required files exist
- [x] CLI command runs end-to-end from YAML
- [x] `summary.json` includes gate-level statuses
- [x] Smoke CI run is green
- [ ] At least one full matrix run artifact checked in

---

## 4) Physics models (Gemini review requested)

`sim/models/quartz_optics.py` implements:
- Sellmeier equation for fused quartz refractive index vs wavelength
- Depth-dependent scattering (Beer-Lambert)
- Thermal bloom radius (Gaussian thermal diffusion)
- Rayleigh range calculation (validates reference layer count)

Gemini: please verify that the `thermal_bloom_radius()` output feeds
correctly into `sim1_holographic.py`'s corruption model.
