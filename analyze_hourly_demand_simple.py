"""
시간대별/존별 택시 수요 분석 (간단 버전)
"""
import json
import numpy as np

# 데이터 로드
with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("Luxembourg 택시 수요 - 시간대별/존별 분석")
print("=" * 80)

num_regions = 8
demand_data = data['demand']

# ========== 1. 시간대별 각 존의 출발 수요 ==========
print("\n시간대별 각 존의 출발 수요 (Outbound):")
print("=" * 80)
print("시간  ", end="")
for i in range(num_regions):
    print(f"R{i:>7}", end="")
print(f"{'총계':>10}")
print("-" * 80)

hourly_origin_demand = np.zeros((24, num_regions))

for hour in range(24):
    hour_data = demand_data[hour]
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            hourly_origin_demand[hour, o] += value

for hour in range(24):
    print(f"{hour:02d}:00 ", end="")
    row_sum = 0
    for i in range(num_regions):
        val = hourly_origin_demand[hour, i]
        print(f"{val:>7.0f}", end="")
        row_sum += val
    print(f"{row_sum:>10.0f}")

# ========== 2. 시간대별 각 존의 도착 수요 ==========
print("\n" + "=" * 80)
print("시간대별 각 존의 도착 수요 (Inbound):")
print("=" * 80)
print("시간  ", end="")
for i in range(num_regions):
    print(f"R{i:>7}", end="")
print(f"{'총계':>10}")
print("-" * 80)

hourly_dest_demand = np.zeros((24, num_regions))

for hour in range(24):
    hour_data = demand_data[hour]
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            hourly_dest_demand[hour, d] += value

for hour in range(24):
    print(f"{hour:02d}:00 ", end="")
    row_sum = 0
    for i in range(num_regions):
        val = hourly_dest_demand[hour, i]
        print(f"{val:>7.0f}", end="")
        row_sum += val
    print(f"{row_sum:>10.0f}")

# ========== 3. 존별 통계 ==========
print("\n" + "=" * 80)
print("존별 통계 요약:")
print("=" * 80)

print("\n각 존의 일일 총 수요:")
for i in range(num_regions):
    total_out = hourly_origin_demand[:, i].sum()
    total_in = hourly_dest_demand[:, i].sum()
    net_flow = total_in - total_out
    
    # 피크 시간
    peak_hour = np.argmax(hourly_origin_demand[:, i])
    peak_value = hourly_origin_demand[peak_hour, i]
    
    print(f"  Region {i}:")
    print(f"    출발: {total_out:>8.0f}명 (피크: {peak_hour:02d}:00 - {peak_value:.0f}명)")
    print(f"    도착: {total_in:>8.0f}명")
    print(f"    Net:  {net_flow:>8.0f}명 {'(유입)' if net_flow > 0 else '(유출)'}")

# ========== 4. 대표 시간대 OD Matrix ==========
print("\n" + "=" * 80)
print("대표 시간대 OD Matrix:")
print("=" * 80)

peak_hours = [7, 12, 17]

for hour in peak_hours:
    print(f"\n{hour:02d}:00 시 (출근/점심/퇴근):")
    print("     ", end="")
    for d in range(num_regions):
        print(f"D{d:>6}", end="")
    print()
    print("-" * 60)
    
    hour_data = demand_data[hour]
    od_matrix = np.zeros((num_regions, num_regions))
    
    for key, value in hour_data.items():
        if ',' in key:
            o, d = map(int, key.split(','))
            od_matrix[o, d] = value
    
    for o in range(num_regions):
        print(f"O{o}   ", end="")
        for d in range(num_regions):
            print(f"{od_matrix[o, d]:>6.0f}", end="")
        print()

# ========== 5. CSV 저장 ==========
print("\n" + "=" * 80)
print("CSV 파일 저장:")
print("=" * 80)

# 출발 수요
with open('saved_files/demand_outbound_hourly.csv', 'w') as f:
    f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + "\n")
    for hour in range(24):
        f.write(f"{hour:02d}:00,")
        f.write(",".join([f"{hourly_origin_demand[hour, i]:.0f}" for i in range(num_regions)]))
        f.write("\n")
print("✅ saved_files/demand_outbound_hourly.csv")

# 도착 수요
with open('saved_files/demand_inbound_hourly.csv', 'w') as f:
    f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + "\n")
    for hour in range(24):
        f.write(f"{hour:02d}:00,")
        f.write(",".join([f"{hourly_dest_demand[hour, i]:.0f}" for i in range(num_regions)]))
        f.write("\n")
print("✅ saved_files/demand_inbound_hourly.csv")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
