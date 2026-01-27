import json
import numpy as np
from collections import defaultdict

# Load JSON
with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

# Analyze demand distribution by region
demand_by_od = defaultdict(list)
demand_by_origin = defaultdict(list)
demand_by_time = defaultdict(list)

for item in data['demand']:
    o, d, t, demand = item['origin'], item['destination'], item['time_stamp'], item['demand']
    if o != d:  # Exclude same region
        demand_by_od[(o, d)].append(demand)
        demand_by_origin[o].append(demand)
        demand_by_time[t].append(demand)

print("=" * 60)
print("DEMAND DISTRIBUTION ANALYSIS")
print("=" * 60)

# Total statistics
all_demands = [item['demand'] for item in data['demand'] if item['origin'] != item['destination']]
print(f"\nTotal OD pairs (excluding o=d): {len(all_demands)}")
print(f"Zero/minimal demands (≤0.0001): {sum(1 for d in all_demands if d <= 0.0001)}")
print(f"Non-zero demands: {sum(1 for d in all_demands if d > 0.0001)}")
print(f"Mean demand (non-zero): {np.mean([d for d in all_demands if d > 0.0001]):.4f}")
print(f"Std demand (non-zero): {np.std([d for d in all_demands if d > 0.0001]):.4f}")
print(f"Max demand: {max(all_demands):.4f}")

# By origin region
print("\n" + "=" * 60)
print("DEMAND BY ORIGIN REGION")
print("=" * 60)
for o in range(8):
    demands = [d for d in demand_by_origin[o] if d > 0.0001]
    if demands:
        print(f"Region {o}: mean={np.mean(demands):.4f}, std={np.std(demands):.4f}, count={len(demands)}")

# Check if sampling is uniform
print("\n" + "=" * 60)
print("SAMPLING UNIFORMITY CHECK")
print("=" * 60)
origin_means = []
for o in range(8):
    demands = [d for d in demand_by_origin[o] if d > 0.0001]
    if demands:
        origin_means.append(np.mean(demands))

print(f"Mean of regional means: {np.mean(origin_means):.4f}")
print(f"Std of regional means: {np.std(origin_means):.4f}")
print(f"CV (Coefficient of Variation): {np.std(origin_means)/np.mean(origin_means):.4f}")
print(f"\nIf CV > 0.3: significant regional bias")
print(f"If CV < 0.1: relatively uniform sampling")
