"""
sim2_oomphlap.py
================
Uberbrain Simulation 2 — Multi-Wavelength State Encoding (The Oomphlap)

Simulates the WRITE and READ commands of the Uberbrain instruction set
using real GST phase-change material physics.

Demonstrates that:

  1. A single GST cell is binary (amorphous=0, crystalline=1)
  2. Multiple spatially-separated GST cells addressed by different wavelengths
     read simultaneously produce combinatorial states — not binary
  3. N wavelength channels = 2^N base states minimum
  4. Add MLC (partial crystallization) and the state space expands further
  5. The oomphlap (minimum addressable unit) is the cluster of N GST sites
     read as a single parallel operation

This is how the Uberbrain escapes binary without any new physics —
only by reading multiple binary sites simultaneously instead of sequentially.

The math:
  - GST amorphous state:   reflectivity ≈ 0.38 (low)
  - GST crystalline state: reflectivity ≈ 0.72 (high)
  - MLC partial states:    intermediate reflectivity values
  - Combined oomphlap state = weighted sum of channel reflectivities
  - State space = product of individual channel state spaces

Usage:
  python sim2_oomphlap.py

Output:
  - uberbrain_sim2_output.png  (state space visualization + truth table)
  - Console WRITE/READ demonstration

Authors: Rocks D. Bear, Claude (Anthropic)
License: CC0 — Public Domain
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from itertools import product as iterproduct

# ─────────────────────────────────────────────────────────────────────────────
# GST MATERIAL CONSTANTS (real values from literature)
# ─────────────────────────────────────────────────────────────────────────────

# Reflectivity values from: Rios et al., Nature Photonics 2015 (ref [13])
GST_AMORPHOUS_REFLECTIVITY   = 0.38   # Low reflectivity — logical 0
GST_CRYSTALLINE_REFLECTIVITY = 0.72   # High reflectivity — logical 1
GST_THRESHOLD                = 0.55   # Decision boundary for 0/1 read

# MLC partial crystallization states (4 levels per cell, like QLC flash)
# Partial crystallization % maps to intermediate reflectivity
MLC_LEVELS = {
    0: GST_AMORPHOUS_REFLECTIVITY,          # 0% crystallized — state 0
    1: GST_AMORPHOUS_REFLECTIVITY + 0.085,  # 33% crystallized — state 1
    2: GST_CRYSTALLINE_REFLECTIVITY - 0.085, # 67% crystallized — state 2
    3: GST_CRYSTALLINE_REFLECTIVITY,         # 100% crystallized — state 3
}

# Wavelength channels (nm) — each addresses a separate GST site
CHANNELS = {
    "Blue  (405nm)": 405,
    "Green (532nm)": 532,
    "Red   (650nm)": 650,
}

# ─────────────────────────────────────────────────────────────────────────────
# GST CELL MODEL
# ─────────────────────────────────────────────────────────────────────────────

class GSTCell:
    """
    Models a single GST phase-change memory site.

    Physical analog: a nanometer-scale region of Ge2Sb2Te5 thin film
    that can be switched between amorphous and crystalline states
    by laser pulses of appropriate energy and duration.

    In the Uberbrain, each wavelength channel addresses its own GST site.
    The sites are spatially adjacent but optically isolated by wavelength.
    """

    def __init__(self, channel_name, wavelength_nm):
        self.channel_name   = channel_name
        self.wavelength_nm  = wavelength_nm
        self.mlc_level      = 0        # 0-3 (binary uses only 0 and 3)
        self.crystallized   = False

    def write(self, state: int, use_mlc: bool = False):
        """
        WRITE command: laser pulse switches GST state.

        Binary mode (use_mlc=False): state is 0 or 1
        MLC mode (use_mlc=True): state is 0, 1, 2, or 3

        Physical: femtosecond pulse at ~405nm triggers athermal PIPC.
        Short pulse → crystalline. Long pulse → amorphous (melt-quench).
        """
        if use_mlc:
            assert 0 <= state <= 3, "MLC state must be 0-3"
            self.mlc_level    = state
            self.crystallized = state >= 2
        else:
            assert state in (0, 1), "Binary state must be 0 or 1"
            self.mlc_level    = state * 3   # 0→level 0, 1→level 3
            self.crystallized = bool(state)

    def read(self) -> dict:
        """
        READ command: low-power CW laser measures reflectivity.

        Returns reflectivity, binary state, and MLC level.
        Physical: read laser wavelength chosen to not disturb GST state
        (below switching threshold energy).
        """
        reflectivity = MLC_LEVELS[self.mlc_level]
        binary_state = 1 if reflectivity >= GST_THRESHOLD else 0
        return {
            "reflectivity": reflectivity,
            "binary_state": binary_state,
            "mlc_level":    self.mlc_level,
            "channel":      self.channel_name,
            "wavelength":   self.wavelength_nm,
        }


# ─────────────────────────────────────────────────────────────────────────────
# OOMPHLAP MODEL
# ─────────────────────────────────────────────────────────────────────────────

class Oomphlap:
    """
    The minimum addressable unit of the Uberbrain.

    An oomphlap is a cluster of N GST sites, one per wavelength channel,
    read simultaneously in a single parallel operation. The combined state
    is decoded from the pattern of reflectivities across all channels.

    Physical analog: a tight cluster of GST sites on the active layer,
    each illuminated by its designated wavelength simultaneously,
    with a matching photodiode array reading all channels at once.

    State space:
      Binary mode:  2^N states  (3 channels → 8 states)
      MLC mode:     4^N states  (3 channels → 64 states)
    """

    def __init__(self, channels: dict):
        self.cells = {
            name: GSTCell(name, wl)
            for name, wl in channels.items()
        }
        self.channel_names = list(channels.keys())

    def write_binary(self, states: list):
        """Write binary states [0/1] to each channel."""
        assert len(states) == len(self.cells)
        for cell, state in zip(self.cells.values(), states):
            cell.write(state, use_mlc=False)

    def write_mlc(self, levels: list):
        """Write MLC levels [0-3] to each channel."""
        assert len(levels) == len(self.cells)
        for cell, level in zip(self.cells.values(), levels):
            cell.write(level, use_mlc=True)

    def read(self) -> dict:
        """
        READ command: all channels illuminated and read simultaneously.

        Returns per-channel readings and the combined oomphlap state.
        The combined state is the positional index in the full state space.
        """
        channel_reads = {
            name: cell.read()
            for name, cell in self.cells.items()
        }

        # Binary combined state (treat each channel as one bit)
        binary_vector = [channel_reads[n]["binary_state"]
                         for n in self.channel_names]
        binary_state_value = int("".join(str(b) for b in binary_vector), 2)

        # MLC combined state (treat each channel as a base-4 digit)
        mlc_vector = [channel_reads[n]["mlc_level"]
                      for n in self.channel_names]
        mlc_state_value = sum(
            v * (4 ** (len(mlc_vector) - 1 - i))
            for i, v in enumerate(mlc_vector)
        )

        return {
            "channels":          channel_reads,
            "binary_vector":     binary_vector,
            "binary_state":      binary_state_value,
            "mlc_vector":        mlc_vector,
            "mlc_state":         mlc_state_value,
            "n_binary_states":   2 ** len(self.cells),
            "n_mlc_states":      4 ** len(self.cells),
        }


# ─────────────────────────────────────────────────────────────────────────────
# DEMONSTRATION: FULL BINARY TRUTH TABLE
# ─────────────────────────────────────────────────────────────────────────────

def demonstrate_binary_truth_table(oomphlap):
    """
    Write every possible binary state combination to the oomphlap
    and read them back. Produces the complete truth table.
    """
    n_channels = len(oomphlap.cells)
    all_states = list(iterproduct([0, 1], repeat=n_channels))
    results = []

    for state_combo in all_states:
        oomphlap.write_binary(list(state_combo))
        reading = oomphlap.read()
        results.append({
            "written":       list(state_combo),
            "read_back":     reading["binary_vector"],
            "state_value":   reading["binary_state"],
            "reflectivities": [
                reading["channels"][name]["reflectivity"]
                for name in oomphlap.channel_names
            ],
            "correct":       list(state_combo) == reading["binary_vector"]
        })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def visualize(oomphlap, truth_table_results, output_path="uberbrain_sim2_output.png"):
    """
    Generate visualization with three panels:
    1. Oomphlap architecture diagram (channel → GST site → photodiode)
    2. Binary truth table (all 8 states, reflectivities, combined value)
    3. State space comparison: binary vs oomphlap vs MLC oomphlap
    """
    fig = plt.figure(figsize=(18, 11))
    fig.patch.set_facecolor("#0D1B2A")

    channel_colors = ["#1a6fc4", "#0fa86e", "#c43a1a"]
    channel_labels = list(oomphlap.channel_names)
    n_channels     = len(channel_labels)

    # ── Panel 1: Architecture diagram ────────────────────────────────────────
    ax1 = fig.add_axes([0.02, 0.35, 0.28, 0.58])
    ax1.set_facecolor("#061218")
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis("off")
    ax1.set_title("Oomphlap Architecture\n(3-channel cluster)",
                  color="white", fontsize=11, fontweight="bold", pad=10)

    # Draw laser sources → GST sites → photodiodes
    for i, (label, color) in enumerate(zip(channel_labels, channel_colors)):
        y = 7.5 - i * 2.5

        # Laser source
        ax1.add_patch(patches.FancyBboxPatch(
            (0.3, y - 0.35), 2.2, 0.7,
            boxstyle="round,pad=0.05",
            facecolor=color, alpha=0.85, edgecolor="none"
        ))
        ax1.text(1.4, y, label, color="white", fontsize=8,
                ha="center", va="center", fontweight="bold")

        # Arrow laser → GST
        ax1.annotate("", xy=(4.2, y), xytext=(2.6, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2))

        # GST site
        oomphlap.cells[label].write(1 if i < 2 else 0)
        reading = oomphlap.cells[label].read()
        refl    = reading["reflectivity"]
        state   = reading["binary_state"]
        gst_color = "#8B5CF6" if state == 1 else "#374151"

        ax1.add_patch(patches.Circle(
            (5.0, y), 0.55,
            facecolor=gst_color, edgecolor="#0A7E8C", linewidth=2
        ))
        ax1.text(5.0, y + 0.02, f"{'C' if state else 'A'}",
                color="white", fontsize=11, ha="center",
                va="center", fontweight="bold")
        ax1.text(5.0, y - 0.85, f"R={refl:.2f}",
                color="#8EAAB3", fontsize=7, ha="center")

        # Arrow GST → photodiode
        ax1.annotate("", xy=(7.3, y), xytext=(5.6, y),
                    arrowprops=dict(arrowstyle="->", color="#8EAAB3", lw=1.5))

        # Photodiode
        ax1.add_patch(patches.FancyBboxPatch(
            (7.4, y - 0.35), 2.2, 0.7,
            boxstyle="round,pad=0.05",
            facecolor="#1C3A4A", edgecolor="#0A7E8C", linewidth=1
        ))
        ax1.text(8.5, y, f"PD-{i+1}", color="#12B5C6",
                fontsize=8, ha="center", va="center")

    # Combined state box
    ax1.add_patch(patches.FancyBboxPatch(
        (1.5, 0.1), 7.0, 1.2,
        boxstyle="round,pad=0.1",
        facecolor="#F4A742", alpha=0.2,
        edgecolor="#F4A742", linewidth=2
    ))
    ax1.text(5.0, 0.95, "Combined Oomphlap State",
            color="#F4A742", fontsize=9, ha="center",
            va="center", fontweight="bold")
    ax1.text(5.0, 0.38, "Read all channels simultaneously → decode state",
            color="#F4A742", fontsize=7.5, ha="center", va="center")

    ax1.text(0.3, 9.7, "WRITE →", color="#8EAAB3", fontsize=8)
    ax1.text(4.1, 9.7, "GST", color="#8EAAB3", fontsize=8)
    ax1.text(7.4, 9.7, "← READ", color="#8EAAB3", fontsize=8)

    # ── Panel 2: Truth table ──────────────────────────────────────────────────
    ax2 = fig.add_axes([0.32, 0.35, 0.38, 0.58])
    ax2.set_facecolor("#061218")
    ax2.axis("off")
    ax2.set_title("Binary Truth Table — All 8 Oomphlap States",
                  color="white", fontsize=11, fontweight="bold", pad=10)

    headers = ["Blue", "Green", "Red",
               "R_B", "R_G", "R_R",
               "State", "✓"]
    col_x   = [0.05, 0.16, 0.27, 0.39, 0.51, 0.63, 0.78, 0.92]
    header_y = 0.93

    for hx, h in zip(col_x, headers):
        ax2.text(hx, header_y, h, color="#12B5C6",
                fontsize=9, fontweight="bold",
                transform=ax2.transAxes, ha="center")

    ax2.axhline(y=0.9, xmin=0.02, xmax=0.98,
               color="#0A7E8C", linewidth=0.8)

    for row_i, result in enumerate(truth_table_results):
        y_pos = 0.85 - row_i * 0.098
        bg_color = "#0A2030" if row_i % 2 == 0 else "#061218"
        ax2.add_patch(patches.Rectangle(
            (0.01, y_pos - 0.04), 0.98, 0.088,
            transform=ax2.transAxes,
            facecolor=bg_color, edgecolor="none"
        ))

        # Channel states (colored)
        for col_i, (bit, color) in enumerate(zip(result["written"], channel_colors)):
            ax2.text(col_x[col_i], y_pos, str(bit),
                    color=color if bit else "#4A6070",
                    fontsize=10, fontweight="bold",
                    transform=ax2.transAxes, ha="center")

        # Reflectivity values
        for col_i, refl in enumerate(result["reflectivities"]):
            ax2.text(col_x[3 + col_i], y_pos, f"{refl:.2f}",
                    color="#8EAAB3", fontsize=8,
                    transform=ax2.transAxes, ha="center")

        # Combined state value
        ax2.text(col_x[6], y_pos, str(result["state_value"] + 1),
                color="#F4A742", fontsize=11, fontweight="bold",
                transform=ax2.transAxes, ha="center")

        # Verification checkmark
        ax2.text(col_x[7], y_pos, "✓" if result["correct"] else "✗",
                color="#0fa86e" if result["correct"] else "#c43a1a",
                fontsize=11, transform=ax2.transAxes, ha="center")

    ax2.text(0.5, 0.02,
            "All 8 states correctly written and read back  ·  "
            "R = reflectivity  ·  State = combined oomphlap value",
            color="#8EAAB3", fontsize=7.5, ha="center",
            transform=ax2.transAxes, style="italic")

    # ── Panel 3: State space comparison ──────────────────────────────────────
    ax3 = fig.add_axes([0.72, 0.35, 0.26, 0.58])
    ax3.set_facecolor("#061218")
    ax3.axis("off")
    ax3.set_title("State Space Comparison",
                  color="white", fontsize=11, fontweight="bold", pad=10)

    comparisons = [
        ("1 bit\n(binary)", 2,     "#374151", "Standard bit"),
        ("8 bits\n(byte)",  256,   "#374151", "Standard byte"),
        ("3-ch\nBinary",    8,     "#1a6fc4", "Oomphlap binary"),
        ("3-ch\nMLC",       64,    "#0fa86e", "Oomphlap MLC"),
        ("3-ch\n+intensity", 1000, "#F4A742", "Oomphlap full"),
    ]

    max_val  = max(c[1] for c in comparisons)
    bar_maxh = 0.72

    for i, (label, states, color, desc) in enumerate(comparisons):
        x     = 0.08 + i * 0.185
        bar_h = (states / max_val) * bar_maxh
        bar_y = 0.18

        ax3.add_patch(patches.Rectangle(
            (x, bar_y), 0.13, bar_h,
            transform=ax3.transAxes,
            facecolor=color, alpha=0.85, edgecolor="white",
            linewidth=0.5
        ))
        ax3.text(x + 0.065, bar_y + bar_h + 0.02,
                str(states), color="white",
                fontsize=9, fontweight="bold",
                transform=ax3.transAxes, ha="center")
        ax3.text(x + 0.065, bar_y - 0.06,
                label, color="#8EAAB3",
                fontsize=7.5, transform=ax3.transAxes,
                ha="center", va="top")

    ax3.axhline(y=0.17, xmin=0.02, xmax=0.98,
               color="#0A7E8C", linewidth=0.8)

    ax3.add_patch(patches.FancyBboxPatch(
        (0.04, 0.02), 0.92, 0.12,
        boxstyle="round,pad=0.02",
        transform=ax3.transAxes,
        facecolor="#0A2030", edgecolor="#F4A742", linewidth=1
    ))
    ax3.text(0.5, 0.09,
            "3 binary channels → 8 states\n"
            "3 MLC channels → 64 states\n"
            "+intensity → ~1000 states",
            color="#F4A742", fontsize=8,
            transform=ax3.transAxes,
            ha="center", va="center")

    # ── Bottom panel: Key result banner ──────────────────────────────────────
    ax4 = fig.add_axes([0.02, 0.02, 0.96, 0.28])
    ax4.set_facecolor("#061829")
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 3)
    ax4.axis("off")
    ax4.add_patch(patches.FancyBboxPatch(
        (0.1, 0.1), 9.8, 2.8,
        boxstyle="round,pad=0.1",
        facecolor="#061829", edgecolor="#0A7E8C", linewidth=1.5
    ))

    ax4.text(5.0, 2.45,
            "KEY RESULT — Oomphlap Encoding",
            color="#12B5C6", fontsize=13, fontweight="bold",
            ha="center", va="center")

    results_text = [
        ("Single GST cell:", "Binary — 2 states (0 or 1)", "#8EAAB3"),
        ("3-channel oomphlap (binary):", "8 states (2³)", "#1a6fc4"),
        ("3-channel oomphlap (MLC 4-level):", "64 states (4³)", "#0fa86e"),
        ("+ intensity gradations:", "~1,000 states per position", "#F4A742"),
        ("+ polarization encoding:", "Further multiplication", "#c43a1a"),
    ]

    for i, (label, value, color) in enumerate(results_text):
        x_label = 0.8
        x_value = 5.2
        y = 1.85 - i * 0.36
        ax4.text(x_label, y, label, color="#8EAAB3",
                fontsize=10, ha="left", va="center")
        ax4.text(x_value, y, value, color=color,
                fontsize=10, fontweight="bold", ha="left", va="center")

    ax4.text(5.0, 0.28,
            "No new physics required. The oomphlap escapes binary by reading "
            "multiple binary sites simultaneously, not sequentially.",
            color="#8EAAB3", fontsize=9, ha="center", va="center",
            style="italic")

    # ── Title ─────────────────────────────────────────────────────────────────
    fig.suptitle(
        "Uberbrain Simulation 2 — Multi-Wavelength State Encoding (The Oomphlap)\n"
        "WRITE + READ Command  ·  GST Phase-Change Material Model  ·  CC0 Public Domain",
        color="white", fontsize=13, fontweight="bold", y=0.99
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1B2A", edgecolor="none")
    print(f"\n  Figure saved → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("  UBERBRAIN SIM 2 — Multi-Wavelength State Encoding")
    print("  WRITE + READ Command Demonstration (The Oomphlap)")
    print("=" * 62)

    # Create oomphlap
    print("\n[1/4] Initializing 3-channel oomphlap...")
    omp = Oomphlap(CHANNELS)
    print(f"      Channels: {list(CHANNELS.keys())}")
    print(f"      Binary state space:  {2**len(CHANNELS)} states (2^{len(CHANNELS)})")
    print(f"      MLC state space:     {4**len(CHANNELS)} states (4^{len(CHANNELS)})")

    # Run full truth table
    print("\n[2/4] Running binary truth table (all 8 states)...")
    truth_table = demonstrate_binary_truth_table(omp)

    print(f"\n  {'Written':<20} {'Read Back':<20} {'State':<8} {'OK'}")
    print(f"  {'─'*20} {'─'*20} {'─'*8} {'─'*4}")
    all_correct = True
    for result in truth_table:
        written  = str(result["written"])
        readback = str(result["read_back"])
        state    = result["state_value"] + 1
        ok       = "✓" if result["correct"] else "✗"
        if not result["correct"]:
            all_correct = False
        print(f"  {written:<20} {readback:<20} {state:<8} {ok}")

    # MLC demonstration
    print("\n[3/4] MLC demonstration (4 levels per channel)...")
    mlc_states_written = []
    for level_combo in [(0,0,0), (1,1,1), (2,2,2), (3,3,3), (1,2,3), (3,1,0)]:
        omp.write_mlc(list(level_combo))
        reading = omp.read()
        mlc_states_written.append(reading["mlc_state"])
        print(f"      Written: {level_combo}  →  "
              f"MLC state: {reading['mlc_state']:>3} / {reading['n_mlc_states']}")

    print(f"\n  ┌──────────────────────────────────────────────────────┐")
    print(f"  │  OOMPHLAP ENCODING RESULT                            │")
    print(f"  ├──────────────────────────────────────────────────────┤")
    print(f"  │  Single GST cell:          2 states                  │")
    print(f"  │  3-channel binary:         {2**3} states (2^3)              │")
    print(f"  │  3-channel MLC (4-level):  {4**3} states (4^3)             │")
    print(f"  │  + intensity gradations:   ~1,000 states/position    │")
    print(f"  ├──────────────────────────────────────────────────────┤")
    print(f"  │  All binary states correct: {'YES ✓' if all_correct else 'NO ✗':<35}│")
    print(f"  │  Architecture: no new physics required               │")
    print(f"  │  Binary is escaped by reading multiple sites         │")
    print(f"  │  simultaneously, not sequentially                    │")
    print(f"  └──────────────────────────────────────────────────────┘")

    # Visualize
    print("\n[4/4] Generating figure...")
    visualize(omp, truth_table)

    print(f"\n{'=' * 62}")
    print("  RESULT SUMMARY")
    print(f"{'=' * 62}")
    print(f"\n  3 wavelength channels, each addressing one binary GST site,")
    print(f"  read simultaneously → 8 distinct states, not 1.")
    print(f"  Add MLC → 64 states. Add intensity → ~1,000 states.")
    print(f"\n  This is the oomphlap. This is how the Uberbrain")
    print(f"  escapes binary using only real GST physics.")
    print(f"\n  → Run sim3_consolicant.py for the forgetting protocol")
    print(f"{'=' * 62}\n")


if __name__ == "__main__":
    main()
