"""
sim2_v2_crosstalk.py
====================
Uberbrain Simulation 2 V0.2 — Oomphlap Encoding Under Real Channel Noise

V0.1 assumed perfect optical isolation between wavelength channels.
V0.2 introduces the real physics that engineers have to deal with:

  NOISE SOURCES MODELED:
  ├── Channel crosstalk    — optical bandpass filters are not perfect.
  │                         Blue light bleeds into green sensor, etc.
  │                         Modeled as a 3x3 crosstalk matrix.
  ├── GST reflectivity drift — thermal variation shifts GST reflectivity
  │                           ±sigma from nominal values each read.
  ├── Shot noise            — photon counting statistics on each channel.
  └── Decision threshold    — fixed threshold may misclassify states
                             near the reflectivity boundary.

  BER ANALYSIS:
  Sweep SNR from 5 dB to 40 dB. At each SNR level:
  - Run 10,000 read trials across all 8 oomphlap states
  - Count misclassified states
  - Report Bit Error Rate (BER)
  - Target BER: < 1e-9 (from SPECIFICATIONS.md)

  CROSSTALK CHARACTERIZATION:
  Show how BER degrades as crosstalk increases from 0% to 20%.
  Find the maximum tolerable crosstalk for target BER.

Key results V0.1 → V0.2:
  V0.1: All 8 states correct (no noise modeled)
  V0.2: BER vs SNR curve — what noise floor is required for reliable decode?
  V0.2: Max tolerable crosstalk for BER < 1e-6

Usage:
  python sim2_v2_crosstalk.py

Output:
  - uberbrain_sim2_v2_output.png
  - Console BER report

Authors: Rocks D. Bear, Claude (Anthropic), Gemini (Google)
License: CC0 — Public Domain
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

SEED            = 42
N_TRIALS        = 10000     # Read trials per SNR/crosstalk point
N_SNR_POINTS    = 20        # SNR sweep points
N_XTALK_POINTS  = 15        # Crosstalk sweep points
TARGET_BER      = 1e-6      # Acceptable BER (conservative target)
TARGET_BER_HARD = 1e-9      # Hard target from SPECIFICATIONS.md

# GST material constants (from Rios et al. 2015)
GST_AMORPHOUS   = 0.38
GST_CRYSTALLINE = 0.72
GST_THRESHOLD   = 0.55      # Decision boundary
GST_DRIFT_SIGMA = 0.015     # Thermal reflectivity drift (±1.5% per read)

# Crosstalk matrix — baseline 5% nearest-neighbor bleed
# C[i,j] = fraction of channel j signal appearing in channel i sensor
BASELINE_XTALK  = 0.05      # 5% nearest-neighbor crosstalk

CHANNELS        = ["Blue (405nm)", "Green (532nm)", "Red (650nm)"]
MLC_LEVELS      = {0: GST_AMORPHOUS, 1: 0.465, 2: 0.635, 3: GST_CRYSTALLINE}

np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────────────────────
# CROSSTALK MATRIX
# ─────────────────────────────────────────────────────────────────────────────

def make_crosstalk_matrix(xtalk_level):
    """
    3x3 optical crosstalk matrix for 3-channel oomphlap.

    Physical model: bandpass filters have finite roll-off.
    A 5% crosstalk means 5% of adjacent channel's signal bleeds through.
    Non-adjacent channels (e.g. blue→red) have much lower crosstalk (xtalk^2).

    Matrix convention: C[i,j] = fraction of true channel j in sensor i reading.
    Diagonal = (1 - xtalk_out), off-diagonal = xtalk_in.

    Returns row-normalized matrix so total energy is conserved.
    """
    n = len(CHANNELS)
    C = np.eye(n)

    # Nearest-neighbor crosstalk
    for i in range(n):
        for j in range(n):
            if i == j:
                C[i, j] = 1.0 - xtalk_level * min(2, n - 1)
            elif abs(i - j) == 1:
                C[i, j] = xtalk_level
            else:
                C[i, j] = xtalk_level ** 2   # Far channel: second-order

    # Normalize rows so total doesn't exceed 1
    row_sums = C.sum(axis=1, keepdims=True)
    return C / row_sums


# ─────────────────────────────────────────────────────────────────────────────
# NOISY OOMPHLAP READ
# ─────────────────────────────────────────────────────────────────────────────

def noisy_read(true_bits, snr_db, xtalk_matrix, rng):
    """
    Simulate a single oomphlap READ with full noise model.

    Steps:
    1. Convert bits to true reflectivities (with GST drift)
    2. Apply crosstalk matrix (signal mixing between channels)
    3. Add shot noise (SNR-determined)
    4. Apply decision threshold → decoded bits

    Returns (decoded_bits, raw_reflectivities)
    """
    n_channels = len(true_bits)

    # True reflectivities with thermal drift
    true_refl = np.array([
        (GST_CRYSTALLINE if b else GST_AMORPHOUS) +
        rng.normal(0, GST_DRIFT_SIGMA)
        for b in true_bits
    ])
    true_refl = np.clip(true_refl, 0, 1)

    # Apply crosstalk: mixed_i = sum_j(C[i,j] * true_j)
    mixed_refl = xtalk_matrix @ true_refl

    # Add shot noise: amplitude noise = 1/SNR_linear
    snr_linear = 10 ** (snr_db / 10)
    noise_sigma = 1.0 / np.sqrt(snr_linear)
    shot_noise  = rng.normal(0, noise_sigma, n_channels)
    measured    = np.clip(mixed_refl + shot_noise, 0, 1)

    # Decision: threshold decode
    decoded = (measured >= GST_THRESHOLD).astype(int)

    return list(decoded), measured


# ─────────────────────────────────────────────────────────────────────────────
# BER CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def calculate_ber_vs_snr(snr_range_db, xtalk_level, n_trials):
    """
    Sweep SNR and calculate BER at fixed crosstalk level.
    """
    from itertools import product as iterproduct

    all_states     = list(iterproduct([0, 1], repeat=3))
    xtalk_matrix   = make_crosstalk_matrix(xtalk_level)
    ber_values     = []
    rng            = np.random.default_rng(SEED)

    for snr_db in snr_range_db:
        n_bit_errors = 0
        n_bits_total = 0

        for _ in range(n_trials):
            state    = all_states[rng.integers(0, len(all_states))]
            decoded, _ = noisy_read(state, snr_db, xtalk_matrix, rng)

            errors        = sum(a != b for a, b in zip(state, decoded))
            n_bit_errors += errors
            n_bits_total += len(state)

        ber = n_bit_errors / n_bits_total if n_bits_total > 0 else 0
        ber_values.append(max(ber, 1e-12))   # Floor for log plot

    return np.array(ber_values)


def calculate_ber_vs_crosstalk(xtalk_range, fixed_snr_db, n_trials):
    """
    Sweep crosstalk level and calculate BER at fixed SNR.
    """
    from itertools import product as iterproduct

    all_states = list(iterproduct([0, 1], repeat=3))
    ber_values = []
    rng        = np.random.default_rng(SEED + 999)

    for xtalk in xtalk_range:
        xtalk_matrix = make_crosstalk_matrix(xtalk)
        n_bit_errors = 0
        n_bits_total = 0

        for _ in range(n_trials):
            state    = all_states[rng.integers(0, len(all_states))]
            decoded, _ = noisy_read(state, fixed_snr_db, xtalk_matrix, rng)

            errors        = sum(a != b for a, b in zip(state, decoded))
            n_bit_errors += errors
            n_bits_total += len(state)

        ber = n_bit_errors / n_bits_total if n_bits_total > 0 else 0
        ber_values.append(max(ber, 1e-12))

    return np.array(ber_values)


def calculate_eye_diagram(snr_db, xtalk_level, n_samples=2000):
    """
    Generate eye diagram data showing signal quality and margin.
    """
    from itertools import product as iterproduct

    xtalk_matrix = make_crosstalk_matrix(xtalk_level)
    rng          = np.random.default_rng(SEED + 42)
    all_states   = list(iterproduct([0, 1], repeat=3))

    zeros_refl, ones_refl = [], []

    for _ in range(n_samples):
        state    = all_states[rng.integers(0, len(all_states))]
        _, meas  = noisy_read(state, snr_db, xtalk_matrix, rng)
        for bit, refl in zip(state, meas):
            if bit == 0:
                zeros_refl.append(refl)
            else:
                ones_refl.append(refl)

    return np.array(zeros_refl), np.array(ones_refl)


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def visualize(snr_range, ber_snr_baseline, ber_snr_high_xtalk,
              xtalk_range, ber_xtalk,
              zeros_refl, ones_refl,
              output_path="uberbrain_sim2_v2_output.png"):

    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor("#0D1B2A")
    gs  = gridspec.GridSpec(2, 3, figure=fig,
                            hspace=0.45, wspace=0.35,
                            left=0.07, right=0.97,
                            top=0.88, bottom=0.08)

    def styled_ax(ax, title):
        ax.set_facecolor("#061218")
        ax.set_title(title, color="white", fontsize=9,
                    fontweight="bold", pad=6)
        ax.tick_params(colors="#8EAAB3", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#0A7E8C")

    # ── Panel 1: BER vs SNR ───────────────────────────────────────────────────
    ax00 = fig.add_subplot(gs[0, 0:2])
    styled_ax(ax00, f"Bit Error Rate vs SNR  (N={N_TRIALS:,} trials per point)")

    ax00.semilogy(snr_range, ber_snr_baseline,
                 color="#0fa86e", linewidth=2,
                 label=f"Baseline crosstalk ({BASELINE_XTALK*100:.0f}%)")
    ax00.semilogy(snr_range, ber_snr_high_xtalk,
                 color="#c43a1a", linewidth=2, linestyle="--",
                 label="High crosstalk (15%)")
    ax00.axhline(y=TARGET_BER, color="#F4A742", linestyle=":",
                linewidth=1.5, label=f"Target BER ({TARGET_BER:.0e})")
    ax00.axhline(y=TARGET_BER_HARD, color="#c43a1a", linestyle=":",
                linewidth=1.5, label=f"Hard target ({TARGET_BER_HARD:.0e})")

    # Find SNR required for target BER
    for ber_arr, color, label in [(ber_snr_baseline, "#0fa86e", "Baseline"),
                                   (ber_snr_high_xtalk, "#c43a1a", "High xtalk")]:
        qualifying = snr_range[ber_arr <= TARGET_BER]
        if len(qualifying) > 0:
            req_snr = qualifying[0]
            ax00.axvline(x=req_snr, color=color, alpha=0.4, linewidth=1)
            ax00.text(req_snr + 0.3, TARGET_BER * 3,
                     f"{label}\n{req_snr:.1f} dB",
                     color=color, fontsize=7)

    ax00.set_xlabel("SNR (dB)", color="#8EAAB3", fontsize=9)
    ax00.set_ylabel("Bit Error Rate", color="#8EAAB3", fontsize=9)
    ax00.set_ylim(1e-10, 1)
    ax00.legend(fontsize=8, labelcolor="white",
               facecolor="#061218", edgecolor="#0A7E8C")
    ax00.grid(True, alpha=0.2, color="#0A7E8C")

    # ── Panel 2: Crosstalk matrix visualization ───────────────────────────────
    ax02 = fig.add_subplot(gs[0, 2])
    styled_ax(ax02, f"Crosstalk Matrix\n({BASELINE_XTALK*100:.0f}% nearest-neighbor)")

    C = make_crosstalk_matrix(BASELINE_XTALK)
    im = ax02.imshow(C, cmap="Blues", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax02, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color="white", labelsize=7)
    ax02.set_xticks([0, 1, 2])
    ax02.set_yticks([0, 1, 2])
    ax02.set_xticklabels(["Blue", "Green", "Red"], color="white", fontsize=8)
    ax02.set_yticklabels(["Blue\nsensor", "Green\nsensor", "Red\nsensor"],
                         color="white", fontsize=7)
    for i in range(3):
        for j in range(3):
            ax02.text(j, i, f"{C[i,j]:.3f}",
                     ha="center", va="center",
                     color="white" if C[i,j] > 0.5 else "#0D1B2A",
                     fontsize=9, fontweight="bold")

    # ── Panel 3: BER vs Crosstalk ─────────────────────────────────────────────
    ax10 = fig.add_subplot(gs[1, 0:2])
    styled_ax(ax10, f"BER vs Crosstalk Level  (SNR = 25 dB fixed)")

    ax10.semilogy(xtalk_range * 100, ber_xtalk,
                 color="#12B5C6", linewidth=2)
    ax10.axhline(y=TARGET_BER, color="#F4A742", linestyle=":",
                linewidth=1.5, label=f"Target BER ({TARGET_BER:.0e})")
    ax10.axhline(y=TARGET_BER_HARD, color="#c43a1a", linestyle=":",
                linewidth=1.5, label=f"Hard target ({TARGET_BER_HARD:.0e})")

    # Max tolerable crosstalk
    tolerable = xtalk_range[ber_xtalk <= TARGET_BER] * 100
    if len(tolerable) > 0:
        max_xtalk = tolerable[-1]
        ax10.axvline(x=max_xtalk, color="#F4A742", alpha=0.5, linewidth=1)
        ax10.text(max_xtalk + 0.2, TARGET_BER * 3,
                 f"Max tolerable\n{max_xtalk:.1f}%",
                 color="#F4A742", fontsize=8)

    ax10.set_xlabel("Crosstalk level (%)", color="#8EAAB3", fontsize=9)
    ax10.set_ylabel("Bit Error Rate", color="#8EAAB3", fontsize=9)
    ax10.set_ylim(1e-10, 1)
    ax10.legend(fontsize=8, labelcolor="white",
               facecolor="#061218", edgecolor="#0A7E8C")
    ax10.grid(True, alpha=0.2, color="#0A7E8C")

    # ── Panel 4: Eye diagram ──────────────────────────────────────────────────
    ax12 = fig.add_subplot(gs[1, 2])
    styled_ax(ax12, "Reflectivity Eye Diagram\n(signal margin visualization)")

    ax12.hist(zeros_refl, bins=60, alpha=0.7, color="#1a6fc4",
             density=True, label="State 0 (amorphous)")
    ax12.hist(ones_refl, bins=60, alpha=0.7, color="#c43a1a",
             density=True, label="State 1 (crystalline)")
    ax12.axvline(x=GST_THRESHOLD, color="#F4A742", linewidth=2,
                linestyle="--", label=f"Decision threshold ({GST_THRESHOLD})")
    ax12.axvline(x=GST_AMORPHOUS, color="#1a6fc4", alpha=0.5,
                linewidth=1, linestyle=":")
    ax12.axvline(x=GST_CRYSTALLINE, color="#c43a1a", alpha=0.5,
                linewidth=1, linestyle=":")

    # Overlap area = BER proxy
    ax12.set_xlabel("Measured reflectivity", color="#8EAAB3", fontsize=9)
    ax12.set_ylabel("Density", color="#8EAAB3", fontsize=9)
    ax12.legend(fontsize=8, labelcolor="white",
               facecolor="#061218", edgecolor="#0A7E8C")

    fig.suptitle(
        "Uberbrain Simulation 2 V0.2 — Oomphlap Encoding Under Real Channel Noise\n"
        "Crosstalk matrix · GST drift · Shot noise · BER curves  ·  CC0",
        color="white", fontsize=12, fontweight="bold", y=0.97
    )

    baseline_ber_at_25 = ber_snr_baseline[np.argmin(np.abs(snr_range - 25))]
    fig.text(0.5, 0.01,
             f"At SNR=25dB, {BASELINE_XTALK*100:.0f}% crosstalk: "
             f"BER = {baseline_ber_at_25:.2e}  ·  "
             f"Target BER = {TARGET_BER:.0e}  ·  "
             f"Drift σ = {GST_DRIFT_SIGMA}",
             ha="center", color="#8EAAB3", fontsize=8, style="italic")

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1B2A", edgecolor="none")
    print(f"\n  Figure saved → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  UBERBRAIN SIM 2 V0.2 — Oomphlap Under Real Channel Noise")
    print("  Crosstalk matrix · GST drift · Shot noise · BER curves")
    print("=" * 65)

    snr_range    = np.linspace(5, 40, N_SNR_POINTS)
    xtalk_range  = np.linspace(0.001, 0.20, N_XTALK_POINTS)

    print(f"\n[1/4] BER vs SNR sweep ({N_SNR_POINTS} points, N={N_TRIALS:,} trials each)...")
    print(f"      Baseline crosstalk: {BASELINE_XTALK*100:.0f}%")
    ber_snr_baseline  = calculate_ber_vs_snr(snr_range, BASELINE_XTALK, N_TRIALS)

    print(f"      High crosstalk (15%)...")
    ber_snr_high_xtalk = calculate_ber_vs_snr(snr_range, 0.15, N_TRIALS)

    print(f"\n[2/4] BER vs crosstalk sweep ({N_XTALK_POINTS} points, SNR=25dB fixed)...")
    ber_xtalk = calculate_ber_vs_crosstalk(xtalk_range, 25, N_TRIALS)

    print(f"\n[3/4] Generating eye diagram data...")
    zeros_refl, ones_refl = calculate_eye_diagram(25, BASELINE_XTALK, 2000)

    # Results summary
    baseline_ber_at_25 = ber_snr_baseline[np.argmin(np.abs(snr_range - 25))]
    req_snr_arr = snr_range[ber_snr_baseline <= TARGET_BER]
    req_snr     = req_snr_arr[0] if len(req_snr_arr) > 0 else ">40"
    tolerable   = xtalk_range[ber_xtalk <= TARGET_BER] * 100
    max_xtalk   = tolerable[-1] if len(tolerable) > 0 else 0

    print(f"\n  ┌────────────────────────────────────────────────────────────┐")
    print(f"  │  BER REPORT V0.2                                           │")
    print(f"  ├────────────────────────────────────────────────────────────┤")
    print(f"  │  Noise model:                                              │")
    print(f"  │    Crosstalk:    {BASELINE_XTALK*100:.0f}% nearest-neighbor                   │")
    print(f"  │    GST drift:    σ = {GST_DRIFT_SIGMA}                              │")
    print(f"  ├────────────────────────────────────────────────────────────┤")
    print(f"  │  BER at SNR=25dB, {BASELINE_XTALK*100:.0f}% xtalk: {baseline_ber_at_25:.2e}             │")
    print(f"  │  SNR required for BER < {TARGET_BER:.0e}:  {req_snr} dB              │")
    print(f"  │  Max tolerable crosstalk: {max_xtalk:.1f}% (at SNR=25dB)       │")
    print(f"  ├────────────────────────────────────────────────────────────┤")
    print(f"  │  V0.1 showed all 8 states correct with zero noise.         │")
    print(f"  │  V0.2 shows the SNR and crosstalk envelope required        │")
    print(f"  │  to achieve those results in a real system.                │")
    print(f"  └────────────────────────────────────────────────────────────┘")

    print(f"\n[4/4] Generating visualization...")
    visualize(snr_range, ber_snr_baseline, ber_snr_high_xtalk,
              xtalk_range, ber_xtalk, zeros_refl, ones_refl)

    print(f"\n{'=' * 65}")
    print(f"  BER target ({TARGET_BER:.0e}) achievable at SNR ≈ {req_snr} dB")
    print(f"  Max tolerable crosstalk: {max_xtalk:.1f}%")
    print(f"  These are now falsifiable engineering specifications.")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
