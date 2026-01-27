import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Load data
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

print("="*80)
print("HYPOTHESIS TESTING: Endogenous Congestion vs Avoidance Behavior")
print("="*80)

# ============ ANALYSIS 1: Route Frequency vs Congestion ============
print("\n[ANALYSIS 1] Route-level: Trip Count vs Avg Congestion Ratio")
print("-"*80)

edge_stats = df.groupby('edge').agg({
    'congestion_ratio': ['mean', 'std', 'max'],
    'edge': 'count'
}).reset_index(drop=True)
edge_stats.columns = ['avg_ratio', 'std_ratio', 'max_ratio', 'trip_count']
edge_stats['edge'] = df.groupby('edge').groups.keys()

# Filter edges with at least 5 trips for statistical significance
significant_edges = edge_stats[edge_stats['trip_count'] >= 5].copy()

# Correlation analysis
correlation = significant_edges['trip_count'].corr(significant_edges['avg_ratio'])
print(f"\nPearson Correlation (Trip Count vs Avg Congestion): {correlation:.3f}")

if correlation > 0.3:
    print("→ STRONG POSITIVE correlation: More trips = More congestion")
    print("→ SUPPORTS Hypothesis 1 (Endogenous Congestion)")
elif correlation < -0.3:
    print("→ STRONG NEGATIVE correlation: More trips = Less congestion")  
    print("→ SUPPORTS Hypothesis 2 (Avoidance Behavior)")
else:
    print("→ WEAK correlation: No clear pattern")

# Top 10 congested routes
top_congested = significant_edges.nlargest(10, 'avg_ratio')[['edge', 'avg_ratio', 'trip_count']]
print("\nTop 10 Most Congested Routes (>=5 trips):")
print(top_congested.to_string(index=False))

# Top 10 frequent routes
top_frequent = significant_edges.nlargest(10, 'trip_count')[['edge', 'trip_count', 'avg_ratio']]
print("\nTop 10 Most Frequent Routes:")
print(top_frequent.to_string(index=False))

# ============ ANALYSIS 2: Time-based Congestion ============
print("\n\n[ANALYSIS 2] Time-based: Do vehicles avoid congested times?")
print("-"*80)

# Group by time windows (5-min buckets) and edge
df['time_bucket'] = (df['departure_time'] // 5) * 5

# For the most frequent edge, check if congestion leads to reduced future trips
most_frequent_edge = significant_edges.nlargest(1, 'trip_count')['edge'].iloc[0]
edge_time = df[df['edge'] == most_frequent_edge].groupby('time_bucket').agg({
    'congestion_ratio': 'mean',
    'edge': 'count'
}).rename(columns={'edge': 'trip_count'})

if len(edge_time) > 1:
    time_corr = edge_time['trip_count'].corr(edge_time['congestion_ratio'])
    print(f"\nMost frequent route: {most_frequent_edge}")
    print(f"Time correlation (Trip Count vs Congestion): {time_corr:.3f}")
    
    if time_corr > 0.2:
        print("→ More trips in time periods WITH congestion")
        print("→ SUPPORTS Hypothesis 1 (Endogenous Congestion)")
    elif time_corr < -0.2:
        print("→ Fewer trips in time periods WITH congestion")
        print("→ SUPPORTS Hypothesis 2 (Avoidance Behavior)")

# ============ ANALYSIS 3: Sequential Causality ============
print("\n\n[ANALYSIS 3] Sequential: Does congestion at time T reduce trips at T+1?")
print("-"*80)

# For each edge, check if high congestion leads to reduced trips in next time window
edge_causality = []
for edge in significant_edges['edge']:
    edge_df = df[df['edge'] == edge].sort_values('departure_time')
    if len(edge_df) < 10:
        continue
    
    # Rolling window analysis
    edge_df['next_count'] = edge_df.groupby(pd.cut(edge_df['departure_time'], bins=10))['edge'].transform('count').shift(-1)
    
    if edge_df['congestion_ratio'].std() > 0 and edge_df['next_count'].std() > 0:
        causal_corr = edge_df['congestion_ratio'].corr(edge_df['next_count'])
        edge_causality.append({
            'edge': edge,
            'causality_corr': causal_corr,
            'trips': len(edge_df)
        })

if edge_causality:
    causality_df = pd.DataFrame(edge_causality)
    avg_causality = causality_df['causality_corr'].mean()
    print(f"\nAverage causality correlation: {avg_causality:.3f}")
    
    if avg_causality < -0.1:
        print("→ High congestion → Fewer future trips")
        print("→ SUGGESTS Hypothesis 2 (Learning/Avoidance)")
    elif avg_causality > 0.1:
        print("→ High congestion → More future trips")
        print("→ SUGGESTS Hypothesis 1 (Persistent Demand)")

# ============ ANALYSIS 4: Congestion Categories ============
print("\n\n[ANALYSIS 4] Distribution Analysis")
print("-"*80)

# Categorize routes
significant_edges['category'] = pd.cut(
    significant_edges['avg_ratio'],
    bins=[0, 1.0, 1.2, 2.0, 10],
    labels=['Fast (<1.0x)', 'Normal (1.0-1.2x)', 'Congested (1.2-2.0x)', 'Severe (>2.0x)']
)

category_stats = significant_edges.groupby('category').agg({
    'trip_count': ['mean', 'sum'],
    'edge': 'count'
}).round(1)
print("\nTrip Distribution by Congestion Category:")
print(category_stats)

# ============ VISUALIZATION ============
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Hypothesis Testing: Endogenous Congestion vs Avoidance', fontsize=14, fontweight='bold')

# Plot 1: Scatter - Trip Count vs Avg Congestion
ax1 = axes[0, 0]
ax1.scatter(significant_edges['trip_count'], significant_edges['avg_ratio'], alpha=0.6, s=50)
z = np.polyfit(significant_edges['trip_count'], significant_edges['avg_ratio'], 1)
p = np.poly1d(z)
ax1.plot(significant_edges['trip_count'], p(significant_edges['trip_count']), 
         "r--", alpha=0.8, linewidth=2, label=f'Trend (r={correlation:.2f})')
ax1.axhline(y=1.2, color='orange', linestyle='--', alpha=0.5, label='Congestion threshold')
ax1.set_xlabel('Trip Count')
ax1.set_ylabel('Avg Congestion Ratio')
ax1.set_title(f'Route Frequency vs Congestion\n(Correlation: {correlation:.3f})')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Top congested routes
ax2 = axes[0, 1]
top_10_cong = significant_edges.nlargest(10, 'avg_ratio')
colors = ['red' if x > 15 else 'orange' for x in top_10_cong['trip_count']]
ax2.barh(range(len(top_10_cong)), top_10_cong['trip_count'], color=colors)
ax2.set_yticks(range(len(top_10_cong)))
ax2.set_yticklabels([f"{e} ({r:.2f}x)" for e, r in zip(top_10_cong['edge'], top_10_cong['avg_ratio'])], 
                     fontsize=8)
ax2.set_xlabel('Trip Count')
ax2.set_title('Trip Count of Top 10 Most Congested Routes')
ax2.grid(True, alpha=0.3, axis='x')

# Plot 3: Box plot by category
ax3 = axes[1, 0]
categories = ['Fast (<1.0x)', 'Normal (1.0-1.2x)', 'Congested (1.2-2.0x)', 'Severe (>2.0x)']
data_by_cat = [significant_edges[significant_edges['category'] == cat]['trip_count'].values 
               for cat in categories if cat in significant_edges['category'].values]
labels_present = [cat for cat in categories if cat in significant_edges['category'].values]
ax3.boxplot(data_by_cat, labels=labels_present)
ax3.set_ylabel('Trip Count')
ax3.set_title('Trip Count Distribution by Congestion Category')
ax3.grid(True, alpha=0.3, axis='y')
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=15, ha='right', fontsize=8)

# Plot 4: Time series for most frequent edge
ax4 = axes[1, 1]
if len(edge_time) > 1:
    ax4_twin = ax4.twinx()
    line1 = ax4.plot(edge_time.index, edge_time['trip_count'], 'b-o', label='Trip Count', linewidth=2)
    line2 = ax4_twin.plot(edge_time.index, edge_time['congestion_ratio'], 'r-s', label='Avg Congestion', linewidth=2)
    ax4.set_xlabel('Time Bucket (min)')
    ax4.set_ylabel('Trip Count', color='b')
    ax4_twin.set_ylabel('Avg Congestion Ratio', color='r')
    ax4.set_title(f'Time Pattern: {most_frequent_edge}\n(Correlation: {time_corr:.2f})')
    ax4.tick_params(axis='y', labelcolor='b')
    ax4_twin.tick_params(axis='y', labelcolor='r')
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left')
    ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('saved_files/congestion/hypothesis_analysis.png', dpi=300, bbox_inches='tight')
print("\n\nVisualization saved: saved_files/congestion/hypothesis_analysis.png")

# ============ CONCLUSION ============
print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if correlation > 0.3:
    print("\n✅ PRIMARY EVIDENCE: HYPOTHESIS 1 (Endogenous Congestion)")
    print("\nFindings:")
    print("  - Strong positive correlation between trip frequency and congestion")
    print("  - More rebalancing flows → More vehicles on route → Congestion increases")
    print("  - This is ENDOGENOUS: Congestion is CAUSED by the rebalancing policy itself")
    print("\nImplication:")
    print("  - SAC's LP solver does NOT account for congestion from its own actions")
    print("  - The 'desired distribution' creates traffic that delays itself")
    print("  - Static travel times underestimate actual costs")
elif correlation < -0.3:
    print("\n✅ PRIMARY EVIDENCE: HYPOTHESIS 2 (Avoidance Behavior)")
    print("\nFindings:")
    print("  - Negative correlation: Congested routes receive FEWER trips")
    print("  - SAC appears to recognize and avoid congested routes")
    print("\nImplication:")
    print("  - The model has some implicit congestion awareness")
    print("  - But still experiences congestion on unavoidable routes")
else:
    print("\n⚠️  MIXED EVIDENCE: Both patterns present")
    print("\n  - Correlation is weak, suggesting BOTH mechanisms at play")
    print("  - Some routes show endogenous congestion (demand-driven)")
    print("  - Other routes show avoidance behavior (policy-driven)")

print("\n" + "="*80)
