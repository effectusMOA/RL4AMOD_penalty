import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read CSV
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')

# Figure (3x2 grid)
fig, axes = plt.subplots(3, 2, figsize=(16, 14))
fig.suptitle('SAC Rebalancing Congestion Analysis', fontsize=16, fontweight='bold')

# ============ 1. Avg Congestion Ratio Over Time ============
ax1 = axes[0, 0]
time_stats = df.groupby('departure_time').agg({
    'congestion_ratio': 'mean',
    'is_congested': 'mean'
}).reset_index()

ax1.plot(time_stats['departure_time'], time_stats['congestion_ratio'], 
         linewidth=2, color='#1f77b4', label='Avg Congestion Ratio')
ax1.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Baseline (1.0x)')
ax1.axhline(y=1.2, color='orange', linestyle='--', alpha=0.7, label='Congested (1.2x)')
ax1.fill_between(time_stats['departure_time'], 1.0, time_stats['congestion_ratio'], 
                  where=(time_stats['congestion_ratio'] > 1.0), alpha=0.3, color='red')
ax1.set_xlabel('Departure Time (min)', fontsize=11)
ax1.set_ylabel('Congestion Ratio (x)', fontsize=11)
ax1.set_title('1. Average Congestion Ratio Over Time', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# ============ 2. Top 10 Most Congested Routes ============
ax2 = axes[0, 1]
edge_stats = df.groupby('edge').agg({
    'congestion_ratio': 'mean',
    'edge': 'count'
}).rename(columns={'edge': 'count'})
edge_stats = edge_stats[edge_stats['count'] >= 10]  # At least 10 trips
top_edges = edge_stats.nlargest(10, 'congestion_ratio')

colors = ['red' if x > 1.5 else 'orange' if x > 1.2 else 'green' 
          for x in top_edges['congestion_ratio']]
ax2.barh(range(len(top_edges)), top_edges['congestion_ratio'], color=colors)
ax2.set_yticks(range(len(top_edges)))
ax2.set_yticklabels(top_edges.index, fontsize=9)
ax2.axvline(x=1.2, color='orange', linestyle='--', alpha=0.7, linewidth=2)
ax2.set_xlabel('Avg Congestion Ratio (x)', fontsize=11)
ax2.set_title('2. Top 10 Most Congested Routes (>=10 trips)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# ============ 3. Predicted vs Actual Time (Scatter) ============
ax3 = axes[1, 0]
scatter_data = df[df['predicted_time'] > 0]  # Exclude 0
colors_scatter = ['red' if x > 1.2 else 'blue' for x in scatter_data['congestion_ratio']]
ax3.scatter(scatter_data['predicted_time'], scatter_data['actual_time'], 
           alpha=0.4, s=20, c=colors_scatter)
max_time = max(scatter_data['predicted_time'].max(), scatter_data['actual_time'].max())
ax3.plot([0, max_time], [0, max_time], 'k--', alpha=0.5, label='Perfect prediction (y=x)')
ax3.plot([0, max_time], [0, max_time*1.2], 'orange', linestyle='--', 
         alpha=0.5, label='20% delay boundary')
ax3.set_xlabel('Predicted Time (min)', fontsize=11)
ax3.set_ylabel('Actual Time (min)', fontsize=11)
ax3.set_title('3. Predicted vs Actual Travel Time', fontsize=12, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# ============ 4. Congestion Ratio Distribution (Histogram) ============
ax4 = axes[1, 1]
# Exclude 0.0
valid_ratios = df[df['congestion_ratio'] > 0]['congestion_ratio']
ax4.hist(valid_ratios, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
ax4.axvline(x=1.0, color='green', linestyle='--', linewidth=2, label='Baseline (1.0x)')
ax4.axvline(x=1.2, color='orange', linestyle='--', linewidth=2, label='Congested (1.2x)')
ax4.axvline(x=valid_ratios.mean(), color='red', linestyle='-', linewidth=2, 
           label=f'Mean ({valid_ratios.mean():.2f}x)')
ax4.set_xlabel('Congestion Ratio (x)', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('4. Congestion Ratio Distribution', fontsize=12, fontweight='bold')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3, axis='y')

# ============ 5. Top 10 Most Frequent Routes ============
ax5 = axes[2, 0]
edge_counts = df['edge'].value_counts().head(10)
ax5.barh(range(len(edge_counts)), edge_counts.values, color='steelblue')
ax5.set_yticks(range(len(edge_counts)))
ax5.set_yticklabels(edge_counts.index, fontsize=9)
ax5.set_xlabel('Number of Rebalancing Trips', fontsize=11)
ax5.set_title('5. Top 10 Most Frequent Rebalancing Routes', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='x')

# ============ 6. Congestion Category Distribution (Pie) ============
ax6 = axes[2, 1]
categories = pd.cut(df['congestion_ratio'], 
                   bins=[0, 0.5, 1.0, 1.2, 1.5, 2.0, 100],
                   labels=['<0.5x\n(Very Fast)', '0.5-1.0x\n(Fast)', 
                          '1.0-1.2x\n(Normal)', '1.2-1.5x\n(Congested)', 
                          '1.5-2.0x\n(Severe)', '>2.0x\n(Extreme)'])
category_counts = categories.value_counts()
colors_pie = ['darkgreen', 'lightgreen', 'yellow', 'orange', 'orangered', 'darkred']
ax6.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
       colors=colors_pie, startangle=90)
ax6.set_title('6. Congestion Category Distribution', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('saved_files/congestion/congestion_analysis.png', dpi=300, bbox_inches='tight')
print("OK Visualization saved: saved_files/congestion/congestion_analysis.png")

# ============ Print Key Statistics ============
print("\n========== Key Statistics ==========")
print(f"Total rebalancing trips: {len(df)}")
print(f"Congested trips (>20%): {df['is_congested'].sum()} ({df['is_congested'].mean()*100:.1f}%)")
print(f"Mean congestion ratio: {df['congestion_ratio'].mean():.2f}x")
print(f"Median congestion ratio: {df['congestion_ratio'].median():.2f}x")
print(f"Max congestion ratio: {df['congestion_ratio'].max():.2f}x")
print(f"Mean delay: {(df['actual_time'] - df['predicted_time']).mean():.1f} min")
print("="*40)
