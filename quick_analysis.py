import json
from collections import defaultdict

with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

hourly = defaultdict(float)
for entry in data['demand']:
    hour = entry['time_stamp'] // 60
    hourly[hour] += entry['demand']

print("Hour,Demand")
for h in range(24):
    print(f"{h},{hourly[h]:.1f}")
