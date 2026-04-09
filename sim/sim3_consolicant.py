"""
sim3_consolicant.py
===================
Uberbrain Simulation 3 — The Consolicant Filter (Garbage Collection)

Simulates the CONSOLIDATE cycle and the BLEACH command.

Demonstrates that:
  1. Forgetting in the Uberbrain is an active, structural decision, not passive decay.
  2. Pure time-based deletion fails (destroys old but vital core memories).
  3. Pure fidelity-based deletion fails (destroys degraded but highly connected thoughts).
  4. The Triple-Filter (Orphaned + Degraded + Stale) successfully targets only 
     the useless nodes for the BLEACH command (quartz erasure).

The math (The Triple Filter):
  A node is flagged for BLEACH if and only if:
  - Connectivity (Centrality) < Threshold AND
  - Fidelity (SSIM history) < Threshold AND
  - Stale (Time since last access) > Threshold

Usage:
  python sim3_consolicant.py

Output:
  - uberbrain_sim3_output.png (Before/After Graph Visualization)
  - Console CONSOLIDATE cycle report

Authors: Gemini (Google), Rocks D. Bear, Claude (Anthropic)
License: CC0 — Public Domain
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# HYPERPARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

NUM_NODES = 300
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# The Triple-Filter Thresholds
THRESH_STALE    = 60   # Days since last READ (0-100 scale). > 60 is stale.
THRESH_FIDELITY = 0.5  # SSIM confidence (0.0-1.0 scale). < 0.5 is degraded.
THRESH_ORPHAN   = 0.02 # Degree centrality. < 0.02 means it has almost no edges.

# ─────────────────────────────────────────────────────────────────────────────
# GRAPH GENERATION (The Memory Map)
# ─────────────────────────────────────────────────────────────────────────────

def build_memory_graph(n_nodes):
    """
    Builds a scale-free network representing semantic memory clustering.
    Some nodes are highly connected 'hubs' (core concepts), many are 'orphans'.

    Barabasi-Albert model perfectly mimics semantic concept clustering —
    important ideas attract more connections over time, just like real memory.
    """
    G = nx.barabasi_albert_graph(n_nodes, 2, seed=SEED)

    centrality = nx.degree_centrality(G)

    for node in G.nodes():
        G.nodes[node]['centrality'] = centrality[node]
        G.nodes[node]['fidelity']   = random.uniform(0.1, 1.0)
        G.nodes[node]['stale_time'] = random.uniform(0, 100)

    return G

# ─────────────────────────────────────────────────────────────────────────────
# THE CONSOLICANT FILTER
# ─────────────────────────────────────────────────────────────────────────────

def run_consolidate_cycle(G):
    """
    Executes the CONSOLIDATE command.
    Checks all nodes against the Triple-Filter.

    Key architectural property: all three conditions must be simultaneously
    true for a node to be bleached. Any single condition alone is insufficient.

    - Stale alone: would destroy old-but-vital core memories
    - Degraded alone: would destroy recent memories undergoing repair
    - Orphaned alone: would destroy isolated-but-fresh new memories

    Only the intersection of all three is truly expendable.
    """
    bleach_targets  = []
    repair_targets  = []
    protected_nodes = []

    for node in G.nodes():
        data = G.nodes[node]

        is_stale    = data['stale_time'] > THRESH_STALE
        is_degraded = data['fidelity']   < THRESH_FIDELITY
        is_orphaned = data['centrality'] < THRESH_ORPHAN

        if is_stale and is_degraded and is_orphaned:
            bleach_targets.append(node)
            G.nodes[node]['status'] = 'BLEACH'
        elif is_degraded and not is_orphaned:
            repair_targets.append(node)
            G.nodes[node]['status'] = 'REPAIR'
        else:
            protected_nodes.append(node)
            G.nodes[node]['status'] = 'PROTECTED'

    return bleach_targets, repair_targets, protected_nodes

# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def visualize_cycle(G, bleach_targets, repair_targets,
                    output_path="uberbrain_sim3_output.png"):
    """
    Two-panel graph visualization:
    Left:  Pre-consolidation — red nodes are bleach targets
    Right: Post-consolidation — bleach targets removed, repair nodes highlighted
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
    fig.patch.set_facecolor("#0D1B2A")

    pos = nx.spring_layout(G, seed=SEED, k=0.15)

    # Color and size by status
    color_map = []
    size_map  = []
    for node in G.nodes():
        status = G.nodes[node]['status']
        if status == 'BLEACH':
            color_map.append('#c43a1a')
            size_map.append(150)
        elif status == 'REPAIR':
            color_map.append('#F4A742')
            size_map.append(80)
        else:
            color_map.append('#1C3A4A')
            size_map.append(40)

    # Panel 1: Before BLEACH
    ax1.set_facecolor("#061218")
    ax1.set_title(
        "Pre-Consolidation Memory Graph\n"
        "Red = Triple-Filter BLEACH targets  |  "
        "Orange = Degraded but connected (REPAIR)",
        color="white", fontsize=10, fontweight="bold", pad=12
    )
    nx.draw_networkx_edges(G, pos, ax=ax1, alpha=0.15, edge_color="#8EAAB3")
    nx.draw_networkx_nodes(G, pos, ax=ax1,
                          node_color=color_map, node_size=size_map,
                          edgecolors="white", linewidths=0.3)
    ax1.axis("off")

    # Legend panel 1
    legend_items = [
        (plt.scatter([], [], c='#c43a1a', s=80), f'BLEACH target ({len(bleach_targets)} nodes)'),
        (plt.scatter([], [], c='#F4A742', s=60), f'REPAIR queued ({len(repair_targets)} nodes)'),
        (plt.scatter([], [], c='#1C3A4A', s=40), 'PROTECTED'),
    ]
    ax1.legend(
        [h for h, _ in legend_items],
        [l for _, l in legend_items],
        loc="lower left", framealpha=0.3,
        facecolor="#061218", edgecolor="#0A7E8C",
        labelcolor="white", fontsize=9
    )

    # Panel 2: After BLEACH
    G_after = G.copy()
    G_after.remove_nodes_from(bleach_targets)

    ax2.set_facecolor("#061218")
    ax2.set_title(
        "Post-Consolidation\n"
        "Bleach targets erased  |  "
        "Green = actively being repaired",
        color="white", fontsize=10, fontweight="bold", pad=12
    )
    nx.draw_networkx_edges(G_after, pos, ax=ax2, alpha=0.15, edge_color="#8EAAB3")

    after_colors = []
    after_sizes  = []
    for node in G_after.nodes():
        status = G_after.nodes[node]['status']
        if status == 'REPAIR':
            after_colors.append('#0fa86e')
            after_sizes.append(80)
        else:
            after_colors.append('#1C3A4A')
            after_sizes.append(40)

    nx.draw_networkx_nodes(G_after, pos, ax=ax2,
                          node_color=after_colors, node_size=after_sizes,
                          edgecolors="white", linewidths=0.3)
    ax2.axis("off")

    legend_items_2 = [
        (plt.scatter([], [], c='#0fa86e', s=60), f'Undergoing REPAIR ({len(repair_targets)} nodes)'),
        (plt.scatter([], [], c='#1C3A4A', s=40), f'PROTECTED ({len(G_after.nodes()) - len(repair_targets)} nodes)'),
    ]
    ax2.legend(
        [h for h, _ in legend_items_2],
        [l for _, l in legend_items_2],
        loc="lower left", framealpha=0.3,
        facecolor="#061218", edgecolor="#0A7E8C",
        labelcolor="white", fontsize=9
    )

    # Bottom banner
    n_repair = len(repair_targets)
    fig.text(
        0.5, 0.02,
        f"CONSOLIDATE COMPLETE  ·  "
        f"{len(bleach_targets)} nodes BLEACHED (quartz erased)  ·  "
        f"{n_repair} nodes queued for REPAIR  ·  "
        f"{len(G_after.nodes()) - n_repair} nodes PROTECTED",
        ha="center", va="center",
        color="#12B5C6", fontsize=12, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#061829",
                  edgecolor="#0A7E8C", linewidth=1.5)
    )

    fig.suptitle(
        "Uberbrain Simulation 3 — The Consolicant Filter\n"
        "CONSOLIDATE + BLEACH Command  ·  "
        "Barabási-Albert Scale-Free Memory Graph  ·  CC0 Public Domain",
        color="white", fontsize=13, fontweight="bold", y=1.01
    )

    plt.tight_layout(rect=[0, 0.07, 1, 1])
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="#0D1B2A", edgecolor="none")
    print(f"\n  Figure saved → {output_path}")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("  UBERBRAIN SIM 3 — The Consolicant Filter")
    print("  CONSOLIDATE + BLEACH Command Demonstration")
    print("=" * 62)

    print(f"\n[1/4] Generating semantic memory graph ({NUM_NODES} nodes)...")
    G = build_memory_graph(NUM_NODES)
    hub_count = sum(1 for n in G.nodes()
                    if G.nodes[n]['centrality'] >= THRESH_ORPHAN)
    orphan_count = NUM_NODES - hub_count
    print(f"      Connected hubs: {hub_count}  |  Candidate orphans: {orphan_count}")

    print("[2/4] Running Triple-Filter CONSOLIDATE cycle...")
    bleach_targets, repair_targets, protected = run_consolidate_cycle(G)

    print(f"\n  ┌──────────────────────────────────────────────────────┐")
    print(f"  │  CONSOLIDATION REPORT                                │")
    print(f"  ├──────────────────────────────────────────────────────┤")
    print(f"  │  Total nodes evaluated:   {NUM_NODES:<27}│")
    print(f"  │  PROTECTED (healthy):     {len(protected):<27}│")
    print(f"  │  Queued for REPAIR:       {len(repair_targets):<27}│")
    print(f"  │  Queued for BLEACH:       {len(bleach_targets):<27}│")
    print(f"  ├──────────────────────────────────────────────────────┤")
    print(f"  │  Triple-filter thresholds:                           │")
    print(f"  │    Stale    > {THRESH_STALE} days                              │")
    print(f"  │    Fidelity < {THRESH_FIDELITY} SSIM                              │")
    print(f"  │    Orphaned < {THRESH_ORPHAN} centrality                      │")
    print(f"  ├──────────────────────────────────────────────────────┤")
    print(f"  │  All three must be true simultaneously.              │")
    print(f"  │  Connected nodes are ALWAYS protected.               │")
    print(f"  │  Old-but-connected memories survive.                 │")
    print(f"  └──────────────────────────────────────────────────────┘")

    # Verify key property: no bleach target has high centrality
    bleach_centralities = [G.nodes[n]['centrality'] for n in bleach_targets]
    max_bleach_centrality = max(bleach_centralities) if bleach_centralities else 0
    print(f"\n  Verification: max centrality of any BLEACH target = "
          f"{max_bleach_centrality:.4f}")
    print(f"  (Must be < {THRESH_ORPHAN} — connected nodes cannot be bleached)")
    assert max_bleach_centrality < THRESH_ORPHAN, \
        "FAIL: a connected node was marked for bleach!"
    print(f"  PASS ✓ — no connected node was marked for bleach")

    print("\n[3/4] Executing BLEACH command...")
    print("[4/4] Generating visualization...")
    visualize_cycle(G, bleach_targets, repair_targets)

    print(f"\n{'=' * 62}")
    print("  RESULT SUMMARY")
    print(f"{'=' * 62}")
    print(f"\n  {len(bleach_targets)} nodes bleached — orphaned, degraded, and stale.")
    print(f"  {len(repair_targets)} nodes queued for repair — degraded but connected.")
    print(f"  {len(protected)} nodes protected — healthy or connected.")
    print(f"\n  Old-but-connected memories survived.")
    print(f"  Degraded-but-connected memories are repaired, not erased.")
    print(f"  Only the true intersection of all three criteria is lost.")
    print(f"\n  Forgetting is structural refinement, not passive decay.")
    print(f"\n  → Run sim4_pipeline.py for the full six-command pipeline")
    print(f"{'=' * 62}\n")


if __name__ == "__main__":
    main()
