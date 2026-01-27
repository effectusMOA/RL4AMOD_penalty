import pandas as pd
import numpy as np

# Load datasets
print("Loading datasets...")
mpc_file = 'saved_files/congestion/congestion_unknown_20251203_160635.csv'
sac_file = 'saved_files/congestion/congestion_unknown_20251203_161548.csv'

df_mpc = pd.read_csv(mpc_file)
df_sac = pd.read_csv(sac_file)

print(f"MPC trips: {len(df_mpc)}")
print(f"SAC trips: {len(df_sac)}")

# Define time buckets (30-minute intervals for 2 hours = 120 min)
time_buckets = [
    (0, 30, '0-30min'),
    (30, 60, '30-60min'),
    (60, 90, '60-90min'),
    (90, 120, '90-120min')
]

# All possible edges (0->0, 0->1, ..., 7->7)
all_edges = [f"{i}->{j}" for i in range(8) for j in range(8)]

def create_flow_matrix(df, time_buckets, all_edges):
    """
    Create a flow matrix with time buckets as rows and edges as columns
    """
    # Initialize result dataframe
    result = pd.DataFrame(index=[label for _, _, label in time_buckets], 
                         columns=all_edges)
    result = result.fillna(0)
    
    # For each time bucket
    for start_time, end_time, label in time_buckets:
        # Filter trips that departed in this time window
        mask = (df['departure_time'] >= start_time) & (df['departure_time'] < end_time)
        trips_in_window = df[mask]
        
        # Count trips per edge
        edge_counts = trips_in_window['edge'].value_counts()
        
        # Fill in the counts
        for edge in all_edges:
            if edge in edge_counts.index:
                result.loc[label, edge] = int(edge_counts[edge])
            else:
                result.loc[label, edge] = 0
    
    return result

# Create flow matrices
print("\nCreating flow matrices...")
mpc_flows = create_flow_matrix(df_mpc, time_buckets, all_edges)
sac_flows = create_flow_matrix(df_sac, time_buckets, all_edges)

# Save to CSV
print("Saving to CSV...")
mpc_flows.to_csv('saved_files/congestion/mpc_flow_by_time.csv')
sac_flows.to_csv('saved_files/congestion/sac_flow_by_time.csv')

print("✓ Saved: saved_files/congestion/mpc_flow_by_time.csv")
print("✓ Saved: saved_files/congestion/sac_flow_by_time.csv")

# Also create a combined comparison CSV
print("\nCreating combined comparison CSV...")
combined_rows = []

for i, (start, end, label) in enumerate(time_buckets):
    row = {'time_period': label}
    for edge in all_edges:
        row[f'MPC_{edge}'] = mpc_flows.loc[label, edge]
        row[f'SAC_{edge}'] = sac_flows.loc[label, edge]
        row[f'DIFF_{edge}'] = sac_flows.loc[label, edge] - mpc_flows.loc[label, edge]
    combined_rows.append(row)

combined_df = pd.DataFrame(combined_rows)
combined_df.to_csv('saved_files/congestion/combined_flow_comparison.csv', index=False)
print("✓ Saved: saved_files/congestion/combined_flow_comparison.csv")

# Print summary statistics
print("\n" + "="*80)
print("FLOW SUMMARY BY TIME PERIOD")
print("="*80)

for label in [lb for _, _, lb in time_buckets]:
    mpc_total = mpc_flows.loc[label].sum()
    sac_total = sac_flows.loc[label].sum()
    diff = sac_total - mpc_total
    print(f"\n{label}:")
    print(f"  MPC: {int(mpc_total):4d} trips")
    print(f"  SAC: {int(sac_total):4d} trips")
    print(f"  Difference: {int(diff):+4d} trips (SAC {'more' if diff > 0 else 'less'} than MPC)")

# Show top 10 busiest routes for each model
print("\n" + "="*80)
print("TOP 10 BUSIEST ROUTES (Total across all time periods)")
print("="*80)

mpc_totals = mpc_flows.sum(axis=0).sort_values(ascending=False)
sac_totals = sac_flows.sum(axis=0).sort_values(ascending=False)

print("\nMPC Top 10:")
for i, (edge, count) in enumerate(mpc_totals.head(10).items(), 1):
    print(f"  {i:2d}. {edge}: {int(count):3d} trips")

print("\nSAC Top 10:")
for i, (edge, count) in enumerate(sac_totals.head(10).items(), 1):
    print(f"  {i:2d}. {edge}: {int(count):3d} trips")

# Calculate routing diversity
print("\n" + "="*80)
print("ROUTING DIVERSITY")
print("="*80)
mpc_used_routes = (mpc_flows.sum(axis=0) > 0).sum()
sac_used_routes = (sac_flows.sum(axis=0) > 0).sum()
print(f"MPC uses {mpc_used_routes}/64 possible routes ({mpc_used_routes/64*100:.1f}%)")
print(f"SAC uses {sac_used_routes}/64 possible routes ({sac_used_routes/64*100:.1f}%)")

# Find most different routes
print("\n" + "="*80)
print("ROUTES WITH BIGGEST DIFFERENCE (SAC - MPC)")
print("="*80)
total_diff = sac_flows.sum(axis=0) - mpc_flows.sum(axis=0)
top_diff = total_diff.sort_values(ascending=False).head(10)
print("\nSAC uses MORE (top 10):")
for edge, diff in top_diff.items():
    if diff > 0:
        sac_count = int(sac_flows[edge].sum())
        mpc_count = int(mpc_flows[edge].sum())
        print(f"  {edge}: +{int(diff):3d} (SAC: {sac_count:3d}, MPC: {mpc_count:3d})")

bottom_diff = total_diff.sort_values(ascending=True).head(10)
print("\nMPC uses MORE (top 10):")
for edge, diff in bottom_diff.items():
    if diff < 0:
        sac_count = int(sac_flows[edge].sum())
        mpc_count = int(mpc_flows[edge].sum())
        print(f"  {edge}: {int(diff):3d} (MPC: {mpc_count:3d}, SAC: {sac_count:3d})")

print("\n" + "="*80)
print("CSV FILES CREATED:")
print("="*80)
print("1. mpc_flow_by_time.csv - MPC flows (4 rows x 64 columns)")
print("2. sac_flow_by_time.csv - SAC flows (4 rows x 64 columns)")
print("3. combined_flow_comparison.csv - Side-by-side comparison")
print("="*80)
