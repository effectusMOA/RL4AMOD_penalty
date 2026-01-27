import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Load both datasets
print("Loading datasets...")
mpc_file = 'saved_files/congestion/congestion_unknown_20251203_160635.csv'
sac_file = 'saved_files/congestion/congestion_unknown_20251203_161548.csv'

df_mpc = pd.read_csv(mpc_file)
df_sac = pd.read_csv(sac_file)

print(f"MPC rebalancing trips: {len(df_mpc)}")
print(f"SAC rebalancing trips: {len(df_sac)}")

# Create comparison visualization (2x3 grid)
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('SAC vs MPC: Rebalancing Congestion Comparison', fontsize=16, fontweight='bold')

# ======== 1. Trip Count Comparison ========
ax1 = axes[0, 0]
models = ['MPC', 'SAC']
trip_counts = [len(df_mpc), len(df_sac)]
colors = ['#3498db', '#e74c3c']
bars = ax1.bar(models, trip_counts, color=colors, alpha=0.7, edgecolor='black')
ax1.set_ylabel('Number of Rebalancing Trips', fontsize=11)
ax1.set_title('1. Total Rebalancing Trips', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')
# Add value labels on bars
for bar, count in zip(bars, trip_counts):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(count)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ======== 2. Average Congestion Ratio ========
ax2 = axes[0, 1]
avg_ratios = [df_mpc['congestion_ratio'].mean(), df_sac['congestion_ratio'].mean()]
bars = ax2.bar(models, avg_ratios, color=colors, alpha=0.7, edgecolor='black')
ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Baseline (1.0x)')
ax2.axhline(y=1.2, color='orange', linestyle='--', alpha=0.7, label='Congested (1.2x)')
ax2.set_ylabel('Average Congestion Ratio', fontsize=11)
ax2.set_title('2. Average Congestion Ratio', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')
for bar, ratio in zip(bars, avg_ratios):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{ratio:.2f}x', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ======== 3. Congestion Distribution ========
ax3 = axes[0, 2]
bins = np.linspace(0, 3, 30)
ax3.hist(df_mpc['congestion_ratio'], bins=bins, alpha=0.5, label='MPC', color='#3498db', edgecolor='black')
ax3.hist(df_sac['congestion_ratio'], bins=bins, alpha=0.5, label='SAC', color='#e74c3c', edgecolor='black')
ax3.axvline(x=1.0, color='green', linestyle='--', alpha=0.7)
ax3.axvline(x=1.2, color='orange', linestyle='--', alpha=0.7)
ax3.set_xlabel('Congestion Ratio', fontsize=11)
ax3.set_ylabel('Frequency', fontsize=11)
ax3.set_title('3. Congestion Ratio Distribution', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# ======== 4. Top Routes Comparison ========
ax4 = axes[1, 0]
# Get top 8 routes by combined usage
mpc_routes = df_mpc['edge'].value_counts().head(8)
sac_routes = df_sac['edge'].value_counts().head(8)
all_routes = set(mpc_routes.index) | set(sac_routes.index)
top_routes = list(all_routes)[:8]

mpc_counts = [mpc_routes.get(r, 0) for r in top_routes]
sac_counts = [sac_routes.get(r, 0) for r in top_routes]

x = np.arange(len(top_routes))
width = 0.35
ax4.barh(x - width/2, mpc_counts, width, label='MPC', color='#3498db', alpha=0.7)
ax4.barh(x + width/2, sac_counts, width, label='SAC', color='#e74c3c', alpha=0.7)
ax4.set_yticks(x)
ax4.set_yticklabels(top_routes, fontsize=9)
ax4.set_xlabel('Number of Trips', fontsize=11)
ax4.set_title('4. Top Routes Usage', fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='x')

# ======== 5. Congestion Rate Comparison ========
ax5 = axes[1, 1]
mpc_congested = (df_mpc['is_congested'].sum() / len(df_mpc) * 100) if len(df_mpc) > 0 else 0
sac_congested = (df_sac['is_congested'].sum() / len(df_sac) * 100) if len(df_sac) > 0 else 0
congested_rates = [mpc_congested, sac_congested]
bars = ax5.bar(models, congested_rates, color=colors, alpha=0.7, edgecolor='black')
ax5.set_ylabel('Congested Trips (%)', fontsize=11)
ax5.set_title('5. Percentage of Congested Trips (>20% delay)', fontsize=12, fontweight='bold')
ax5.set_ylim([0, 100])
ax5.grid(True, alpha=0.3, axis='y')
for bar, rate in zip(bars, congested_rates):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
             f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ======== 6. Average Delay Comparison ========
ax6 = axes[1, 2]
mpc_delay = (df_mpc['actual_time'] - df_mpc['predicted_time']).mean()
sac_delay = (df_sac['actual_time'] - df_sac['predicted_time']).mean()
delays = [mpc_delay, sac_delay]
bars = ax6.bar(models, delays, color=colors, alpha=0.7, edgecolor='black')
ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax6.set_ylabel('Average Delay (minutes)', fontsize=11)
ax6.set_title('6. Average Delay Time', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')
for bar, delay in zip(bars, delays):
    height = bar.get_height()
    va = 'bottom' if delay >= 0 else 'top'
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{delay:.1f} min', ha='center', va=va, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('saved_files/congestion/sac_vs_mpc_comparison.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved: saved_files/congestion/sac_vs_mpc_comparison.png")

# ======== Print Detailed Statistics ========
print("\n" + "="*80)
print("DETAILED COMPARISON: SAC vs MPC")
print("="*80)

print("\n[1] OVERALL STATISTICS")
print("-"*80)
print(f"{'Metric':<40} {'MPC':>15} {'SAC':>15} {'Difference':>10}")
print("-"*80)
print(f"{'Total Rebalancing Trips':<40} {len(df_mpc):>15} {len(df_sac):>15} {len(df_sac)-len(df_mpc):>10}")
print(f"{'Avg Congestion Ratio':<40} {df_mpc['congestion_ratio'].mean():>15.2f} {df_sac['congestion_ratio'].mean():>15.2f} {df_sac['congestion_ratio'].mean()-df_mpc['congestion_ratio'].mean():>10.2f}")
print(f"{'Congested Trips (>20%)':<40} {df_mpc['is_congested'].sum():>15} {df_sac['is_congested'].sum():>15} {df_sac['is_congested'].sum()-df_mpc['is_congested'].sum():>10}")
print(f"{'Congestion Rate (%)':<40} {mpc_congested:>15.1f} {sac_congested:>15.1f} {sac_congested-mpc_congested:>10.1f}")
print(f"{'Avg Delay (min)':<40} {mpc_delay:>15.1f} {sac_delay:>15.1f} {sac_delay-mpc_delay:>10.1f}")
print(f"{'Max Congestion Ratio':<40} {df_mpc['congestion_ratio'].max():>15.2f} {df_sac['congestion_ratio'].max():>15.2f}")

print("\n[2] KEY INSIGHTS")
print("-"*80)

# Insight 1: Rebalancing frequency
ratio = len(df_sac) / len(df_mpc) if len(df_mpc) > 0 else 0
print(f"• SAC performs {ratio:.1f}x MORE rebalancing than MPC ({len(df_sac)} vs {len(df_mpc)} trips)")

# Insight 2: Congestion efficiency
if mpc_congested < sac_congested:
    print(f"• MPC has LOWER congestion rate: {mpc_congested:.1f}% vs SAC {sac_congested:.1f}%")
    print(f"  → MPC is more efficient at avoiding congestion")
else:
    print(f"• SAC has LOWER congestion rate: {sac_congested:.1f}% vs MPC {mpc_congested:.1f}%")
    print(f"  → SAC is more efficient at avoiding congestion")

# Insight 3: Route diversity
mpc_unique = len(df_mpc['edge'].unique())
sac_unique = len(df_sac['edge'].unique())
print(f"• Route diversity: MPC uses {mpc_unique} unique routes, SAC uses {sac_unique} unique routes")

# Insight 4: Delay comparison
if mpc_delay < sac_delay:
    print(f"• MPC has LESS delay: {mpc_delay:.1f} min vs SAC {sac_delay:.1f} min")
else:
    print(f"• SAC has LESS delay: {sac_delay:.1f} min vs MPC {mpc_delay:.1f} min")

print("\n[3] RECOMMENDATIONS")
print("-"*80)
if len(df_sac) > len(df_mpc) * 5:
    print("⚠️  SAC performs excessive rebalancing (>5x more than MPC)")
    print("   → Consider increasing rebalancing cost (beta) to reduce unnecessary trips")
    print("   → Or implement congestion-aware rebalancing in SAC's reward function")

if sac_congested > mpc_congested + 10:
    print("⚠️  SAC experiences significantly more congestion")
    print("   → SAC's aggressive rebalancing creates self-induced congestion")
    print("   → Consider adding congestion penalty to SAC's reward")

if mpc_delay < 0 and sac_delay > 0:
    print("✅ MPC achieves faster-than-predicted travel times")
    print("   → MPC's conservative rebalancing reduces traffic")
    print("   → SAC could learn from MPC's route selection strategy")

print("\n" + "="*80)
