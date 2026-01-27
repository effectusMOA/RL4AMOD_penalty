import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

print("Loading data...")
df = pd.read_csv('saved_files/congestion/congestion_log_20251202_225841.csv')
print(f"Loaded {len(df)} rows")

print("Creating figure...")
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# Simple time series plot
time_stats = df.groupby('departure_time')['congestion_ratio'].mean().reset_index()
ax.plot(time_stats['departure_time'], time_stats['congestion_ratio'], linewidth=2)
ax.axhline(y=1.0, color='green', linestyle='--', label='Baseline')
ax.axhline(y=1.2, color='red', linestyle='--', label='Congested')
ax.set_xlabel('Departure Time (min)')
ax.set_ylabel('Avg Congestion Ratio')
ax.set_title('Congestion Ratio Over Time')
ax.legend()
ax.grid(True, alpha=0.3)

print("Saving figure...")
plt.savefig('saved_files/congestion/test_plot.png', dpi=150, bbox_inches='tight')
print("SUCCESS: Saved to saved_files/congestion/test_plot.png")
