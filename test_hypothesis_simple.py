import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

print("="*60)
print("HYPOTHESIS TESTING")
print("="*60)

# Route-level analysis
edge_stats = df.groupby('edge').agg({
    'congestion_ratio': 'mean',
    'edge': 'count'
}).rename(columns={'edge': 'trip_count', 'congestion_ratio': 'avg_ratio'})

# Filter significant routes (>=5 trips)
significant = edge_stats[edge_stats['trip_count'] >= 5]

# Calculate correlation
correlation = significant['trip_count'].corr(significant['avg_ratio'])

print(f"\nCorrelation (Frequency vs Congestion): {correlation:.3f}")
print("\nInterpretation:")

if correlation > 0.3:
    print("  STRONG POSITIVE → More trips = More congestion")
    print("  → SUPPORTS Hypothesis 1: ENDOGENOUS CONGESTION")
    print("  → Rebalancing flow CAUSES congestion")
elif correlation < -0.3:
    print("  STRONG NEGATIVE → More trips = Less congestion")
    print("  → SUPPORTS Hypothesis 2: AVOIDANCE BEHAVIOR")  
    print("  → SAC avoids congested routes")
else:
    print("  WEAK → Mixed evidence")

# Top congested routes
print("\n" + "-"*60)
print("Top 10 Most Congested Routes:")
print("-"*60)
top_cong = significant.nlargest(10, 'avg_ratio')
for idx, (edge, row) in enumerate(top_cong.iterrows(), 1):
    print(f"{idx}. {edge}: {row['avg_ratio']:.2f}x (trips: {int(row['trip_count'])})")

# Top frequent routes  
print("\n" + "-"*60)
print("Top 10 Most Frequent Routes:")
print("-"*60)
top_freq = significant.nlargest(10, 'trip_count')
for idx, (edge, row) in enumerate(top_freq.iterrows(), 1):
    print(f"{idx}. {edge}: {int(row['trip_count'])} trips (avg: {row['avg_ratio']:.2f}x)")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)

if correlation > 0.3:
    print("\nHypothesis 1 (ENDOGENOUS CONGESTION) is SUPPORTED")
    print("\nEvidence:")
    print("- Busy routes have HIGHER congestion")
    print("- SAC sends many vehicles to same destination")
    print("- This creates traffic congestion")
    print("\nImplication:")
    print("- LP solver uses STATIC travel time")
    print("- Does NOT account for congestion from rebalancing")
    print("- Actual cost is HIGHER than predicted")
elif correlation < -0.3:
    print("\nHypothesis 2 (AVOIDANCE BEHAVIOR) is SUPPORTED")
    print("\nEvidence:")
    print("- Congested routes receive FEWER trips")
    print("- SAC learns to avoid slow routes")
else:
    print("\nMIXED RESULTS")
    print("\nBoth patterns exist:")
    print("- Some routes: endogenous congestion")
    print("- Other routes: avoidance behavior")

print("="*60)
