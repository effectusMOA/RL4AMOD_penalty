import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# Load flow matrices
print("Loading flow matrices...")
mpc_flows = pd.read_csv('saved_files/congestion/mpc_flow_by_time.csv', index_col=0)
sac_flows = pd.read_csv('saved_files/congestion/sac_flow_by_time.csv', index_col=0)

print(f"MPC shape: {mpc_flows.shape}")
print(f"SAC shape: {sac_flows.shape}")

# Convert edge names to origin-destination matrix
def edge_to_matrix(df_row):
    """Convert a row of edge flows to 8x8 matrix"""
    matrix = np.zeros((8, 8))
    for col in df_row.index:
        if '->' in col:
            orig, dest = col.split('->')
            orig, dest = int(orig), int(dest)
            matrix[orig, dest] = df_row[col]
    return matrix

# Time periods
time_periods = ['0-30min', '30-60min', '60-90min', '90-120min']

# Create 2x4 subplots (2 rows: MPC/SAC, 4 cols: time periods)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('Rebalancing Flow Heatmaps: MPC vs SAC', fontsize=16, fontweight='bold')

# Find global max for consistent color scale
all_values = []
for period in time_periods:
    all_values.extend(mpc_flows.loc[period].values)
    all_values.extend(sac_flows.loc[period].values)
vmax = max(all_values)

# Plot heatmaps
for col_idx, period in enumerate(time_periods):
    # MPC heatmap (top row)
    mpc_matrix = edge_to_matrix(mpc_flows.loc[period])
    ax_mpc = axes[0, col_idx]
    im_mpc = ax_mpc.imshow(mpc_matrix, cmap='YlOrRd', vmin=0, vmax=vmax, aspect='auto')
    ax_mpc.set_title(f'MPC: {period}', fontsize=11, fontweight='bold')
    ax_mpc.set_xlabel('Destination Zone', fontsize=10)
    ax_mpc.set_ylabel('Origin Zone', fontsize=10)
    ax_mpc.set_xticks(range(8))
    ax_mpc.set_yticks(range(8))
    # Add text annotations
    for i in range(8):
        for j in range(8):
            text = ax_mpc.text(j, i, f'{int(mpc_matrix[i, j])}',
                              ha="center", va="center", color="black", fontsize=7)
    if col_idx == 3:
        plt.colorbar(im_mpc, ax=ax_mpc)
    
    # SAC heatmap (bottom row)
    sac_matrix = edge_to_matrix(sac_flows.loc[period])
    ax_sac = axes[1, col_idx]
    im_sac = ax_sac.imshow(sac_matrix, cmap='YlGnBu', vmin=0, vmax=vmax, aspect='auto')
    ax_sac.set_title(f'SAC: {period}', fontsize=11, fontweight='bold')
    ax_sac.set_xlabel('Destination Zone', fontsize=10)
    ax_sac.set_ylabel('Origin Zone', fontsize=10)
    ax_sac.set_xticks(range(8))
    ax_sac.set_yticks(range(8))
    # Add text annotations
    for i in range(8):
        for j in range(8):
            text = ax_sac.text(j, i, f'{int(sac_matrix[i, j])}',
                              ha="center", va="center", color="black", fontsize=7)
    if col_idx == 3:
        plt.colorbar(im_sac, ax=ax_sac)

plt.tight_layout()
plt.savefig('saved_files/congestion/flow_heatmaps_by_time.png', dpi=300, bbox_inches='tight')
print("Saved: saved_files/congestion/flow_heatmaps_by_time.png")

# ===== Create total aggregated heatmap (MPC vs SAC vs DIFF) =====
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
fig2.suptitle('Total Rebalancing Flows (All Time Periods)', fontsize=14, fontweight='bold')

# Calculate totals
mpc_total_matrix = np.zeros((8, 8))
sac_total_matrix = np.zeros((8, 8))

for period in time_periods:
    mpc_total_matrix += edge_to_matrix(mpc_flows.loc[period])
    sac_total_matrix += edge_to_matrix(sac_flows.loc[period])

diff_matrix = sac_total_matrix - mpc_total_matrix

# MPC total
ax1 = axes2[0]
im1 = ax1.imshow(mpc_total_matrix, cmap='YlOrRd', vmin=0, aspect='auto')
ax1.set_title(f'MPC Total (n={int(mpc_total_matrix.sum())})', fontsize=12, fontweight='bold')
ax1.set_xlabel('Destination Zone', fontsize=10)
ax1.set_ylabel('Origin Zone', fontsize=10)
ax1.set_xticks(range(8))
ax1.set_yticks(range(8))
for i in range(8):
    for j in range(8):
        ax1.text(j, i, f'{int(mpc_total_matrix[i, j])}',
                ha="center", va="center", color="black", fontsize=8)
plt.colorbar(im1, ax=ax1)

# SAC total
ax2 = axes2[1]
im2 = ax2.imshow(sac_total_matrix, cmap='YlGnBu', vmin=0, aspect='auto')
ax2.set_title(f'SAC Total (n={int(sac_total_matrix.sum())})', fontsize=12, fontweight='bold')
ax2.set_xlabel('Destination Zone', fontsize=10)
ax2.set_ylabel('Origin Zone', fontsize=10)
ax2.set_xticks(range(8))
ax2.set_yticks(range(8))
for i in range(8):
    for j in range(8):
        ax2.text(j, i, f'{int(sac_total_matrix[i, j])}',
                ha="center", va="center", color="black", fontsize=8)
plt.colorbar(im2, ax=ax2)

# Difference (SAC - MPC)
ax3 = axes2[2]
max_abs_diff = max(abs(diff_matrix.min()), abs(diff_matrix.max()))
im3 = ax3.imshow(diff_matrix, cmap='RdBu_r', vmin=-max_abs_diff, vmax=max_abs_diff, aspect='auto')
ax3.set_title('Difference (SAC - MPC)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Destination Zone', fontsize=10)
ax3.set_ylabel('Origin Zone', fontsize=10)
ax3.set_xticks(range(8))
ax3.set_yticks(range(8))
for i in range(8):
    for j in range(8):
        color = 'white' if abs(diff_matrix[i, j]) > max_abs_diff*0.5 else 'black'
        ax3.text(j, i, f'{int(diff_matrix[i, j]):+d}',
                ha="center", va="center", color=color, fontsize=8)
plt.colorbar(im3, ax=ax3)

plt.tight_layout()
plt.savefig('saved_files/congestion/flow_heatmaps_total.png', dpi=300, bbox_inches='tight')
print("Saved: saved_files/congestion/flow_heatmaps_total.png")

# ===== Print key insights =====
print("\n" + "="*80)
print("HEATMAP INSIGHTS")
print("="*80)

# Find most used routes
print("\nMOST USED ROUTES:")
print("-"*80)
mpc_flat = [(i, j, mpc_total_matrix[i, j]) for i in range(8) for j in range(8)]
sac_flat = [(i, j, sac_total_matrix[i, j]) for i in range(8) for j in range(8)]

mpc_top = sorted(mpc_flat, key=lambda x: x[2], reverse=True)[:5]
sac_top = sorted(sac_flat, key=lambda x: x[2], reverse=True)[:5]

print("\nMPC Top 5:")
for i, j, count in mpc_top:
    print(f"  {i}->{j}: {int(count)} trips")

print("\nSAC Top 5:")
for i, j, count in sac_top:
    print(f"  {i}->{j}: {int(count)} trips")

# Find biggest differences
diff_flat = [(i, j, diff_matrix[i, j]) for i in range(8) for j in range(8)]
diff_sorted = sorted(diff_flat, key=lambda x: abs(x[2]), reverse=True)[:10]

print("\n\nBIGGEST DIFFERENCES (SAC - MPC):")
print("-"*80)
for i, j, diff in diff_sorted:
    if diff != 0:
        mpc_val = int(mpc_total_matrix[i, j])
        sac_val = int(sac_total_matrix[i, j])
        print(f"  {i}->{j}: {diff:+.0f} (MPC: {mpc_val}, SAC: {sac_val})")

# Diagonal analysis (same zone)
print("\n\nDIAGONAL (Same-Zone movements):")
print("-"*80)
mpc_diag = sum([mpc_total_matrix[i, i] for i in range(8)])
sac_diag = sum([sac_total_matrix[i, i] for i in range(8)])
print(f"MPC: {int(mpc_diag)} trips ({mpc_diag/mpc_total_matrix.sum()*100:.1f}%)")
print(f"SAC: {int(sac_diag)} trips ({sac_diag/sac_total_matrix.sum()*100:.1f}%)")

# Route diversity
print("\n\nROUTE DIVERSITY:")
print("-"*80)
mpc_used = np.count_nonzero(mpc_total_matrix)
sac_used = np.count_nonzero(sac_total_matrix)
print(f"MPC uses {mpc_used}/64 routes ({mpc_used/64*100:.1f}%)")
print(f"SAC uses {sac_used}/64 routes ({sac_used/64*100:.1f}%)")

print("\n" + "="*80)
print("VISUALIZATION FILES CREATED:")
print("="*80)
print("1. flow_heatmaps_by_time.png - Time-series heatmaps (2x4 grid)")
print("2. flow_heatmaps_total.png - Total aggregated heatmaps (1x3 grid)")
print("="*80)
