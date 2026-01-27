import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

print("Loading data...")
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')
print(f"Loaded {len(df)} rows")

print("Creating visualizations...")
# Figure (3x2 grid)
fig, axes = plt.subplots(3, 2, figsize=(16, 14))
fig.suptitle('SAC Rebalancing Congestion Analysis', fontsize=16, fontweight='bold')

# 1. Avg Congestion Ratio Over Time
print("  Plot 1/6: Time series...")
ax1 = axes[0, 0]
time_stats = df.groupby('departure_time').agg({
    'congestion_ratio': 'mean',
    'is_congested': 'mean'
}).reset_index()

ax1.plot(time_stats['departure_time'], time_stats['congestion_ratio'], 
         linewidth=2, color='#1f77b4', label='Avg Congestion')
ax1.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Baseline (1.0x)')
ax1.axhline(y=1.2, color='orange', linestyle='--', alpha=0.7, label='Congested (1.2x)')
ax1.fill_between(time_stats['departure_time'], 1.0, time_stats['congestion_ratio'], 
                  where=(time_stats['congestion_ratio'] > 1.0), alpha=0.3, color='red')
ax1.set_xlabel('Departure Time (min)', fontsize=11)
ax1.set_ylabel('Congestion Ratio', fontsize=11)
ax1.set_title('1. Avg Congestion Over Time', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# 2. Top 10 Most Congested Routes
print("  Plot 2/6: Top congested routes...")
ax2 = axes[0, 1]
edge_stats = df.groupby('edge').agg({
    'congestion_ratio': 'mean',
    'edge': 'count'
}).rename(columns={'edge': 'count'})
edge_stats = edge_stats[edge_stats['count'] >= 10]
top_edges = edge_stats.nlargest(10, 'congestion_ratio')

colors = ['red' if x > 1.5 else 'orange' if x > 1.2 else 'green' 
          for x in top_edges['congestion_ratio']]
ax2.barh(range(len(top_edges)), top_edges['congestion_ratio'], color=colors)
ax2.set_yticks(range(len(top_edges)))
ax2.set_yticklabels(top_edges.index, fontsize=9)
ax2.axvline(x=1.2, color='orange', linestyle='--', alpha=0.7, linewidth=2)
ax2.set_xlabel('Avg Congestion Ratio', fontsize=11)
ax2.set_title('2. Top 10 Congested Routes (>=10 trips)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# 3. Predicted vs Actual Time
print("  Plot 3/6: Scatter plot...")
ax3 = axes[1, 0]
scatter_data = df[df['predicted_time'] > 0]
colors_scatter = ['red' if x > 1.2 else 'blue' for x in scatter_data['congestion_ratio']]
ax3.scatter(scatter_data['predicted_time'], scatter_data['actual_time'], 
           alpha=0.4, s=20, c=colors_scatter)
max_time = max(scatter_data['predicted_time'].max(), scatter_data['actual_time'].max())
ax3.plot([0, max_time], [0, max_time], 'k--', alpha=0.5, label='Perfect (y=x)')
ax3.plot([0, max_time], [0, max_time*1.2], 'orange', linestyle='--', 
         alpha=0.5, label='20% delay')
ax3.set_xlabel('Predicted Time (min)', fontsize=11)
ax3.set_ylabel('Actual Time (min)', fontsize=11)
ax3.set_title('3. Predicted vs Actual Time', fontsize=12, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# 4. Distribution
print("  Plot 4/6: Histogram...")
ax4 = axes[1, 1]
valid_ratios = df[df['congestion_ratio'] > 0]['congestion_ratio']
ax4.hist(valid_ratios, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
ax4.axvline(x=1.0, color='green', linestyle='--', linewidth=2, label='Baseline')
ax4.axvline(x=1.2, color='orange', linestyle='--', linewidth=2, label='Congested')
ax4.axvline(x=valid_ratios.mean(), color='red', linestyle='-', linewidth=2, 
           label=f'Mean ({valid_ratios.mean():.2f}x)')
ax4.set_xlabel('Congestion Ratio', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('4. Congestion Distribution', fontsize=12, fontweight='bold')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3, axis='y')

# 5. Most Frequent Routes
print("  Plot 5/6: Frequent routes...")
ax5 = axes[2, 0]
edge_counts = df['edge'].value_counts().head(10)
ax5.barh(range(len(edge_counts)), edge_counts.values, color='steelblue')
ax5.set_yticks(range(len(edge_counts)))
ax5.set_yticklabels(edge_counts.index, fontsize=9)
ax5.set_xlabel('Number of Trips', fontsize=11)
ax5.set_title('5. Top 10 Frequent Routes', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='x')

# 6. Category Pie Chart
print("  Plot 6/6: Pie chart...")
ax6 = axes[2, 1]
categories = pd.cut(df['congestion_ratio'], 
                   bins=[0, 0.5, 1.0, 1.2, 1.5, 2.0, 100],
                   labels=['<0.5x\\n(Fast)', '0.5-1.0x\\n(Quick)', 
                          '1.0-1.2x\\n(Normal)', '1.2-1.5x\\n(Slow)', 
                          '1.5-2.0x\\n(Very Slow)', '>2.0x\\n(Extreme)'])
category_counts = categories.value_counts()
colors_pie = ['darkgreen', 'lightgreen', 'yellow', 'orange', 'orangered', 'darkred']
ax6.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
       colors=colors_pie, startangle=90)
ax6.set_title('6. Category Distribution', fontsize=12, fontweight='bold')

print("Saving figure...")
plt.tight_layout()
plt.savefig('saved_files/congestion/congestion_analysis.png', dpi=300, bbox_inches='tight')
print("SUCCESS saved: saved_files/congestion/congestion_analysis.png")

# Statistics
print("\n========== Statistics ==========")
print(f"Total trips: {len(df)}")
print(f"Congested (>20%%): {df['is_congested'].sum()} ({df['is_congested'].mean()*100:.1f}%%)")
print(f"Mean ratio: {df['congestion_ratio'].mean():.2f}x")
print(f"Median ratio: {df['congestion_ratio'].median():.2f}x")
print(f"Max ratio: {df['congestion_ratio'].max():.2f}x")
print(f"Mean delay: {(df['actual_time'] - df['predicted_time']).mean():.1f} min")
print("="*40)
