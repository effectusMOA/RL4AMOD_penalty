"""
시간대별/존별 택시 수요 분석 - 수정 버전
"""
import json
import numpy as np

# 데이터 로드
print("데이터 로딩 중...")
with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("Luxembourg 택시 수요 - 시간대별/존별 분석")
print("=" * 80)

num_regions = 8

# demand 데이터 구조 확인
print(f"\n데이터 구조:")
print(f"  Keys: {list(data.keys())}")
print(f"  Demand is list: {isinstance(data['demand'], list)}")
print(f"  Length: {len(data['demand'])}")

demand_data = data['demand']

# ========== 샘플 확인 ==========
print(f"\n샘플 데이터 (0시):")
if isinstance(demand_data[0], dict):
    sample_items = list(demand_data[0].items())[:10]
    for key, value in sample_items:
        print(f"  {key}: {value}")

# ========== 1. 시간대별 각 존의 출발 수요 ==========
print("\n" + "=" * 80)
print("시간대별 각 존의 출발 수요 (Outbound):")
print("=" * 80)
print("시간  ", end="")
for i in range(num_regions):
    print(f"R{i:>7}", end="")
print(f"{'총계':>10}")
print("-" * 80)

hourly_origin_demand = np.zeros((24, num_regions))

# 데이터 파싱 - 딕셔너리 확인
for hour in range(24):
    if hour >= len(demand_data):
        break
    hour_data = demand_data[hour]
    
    if isinstance(hour_data, dict):
        for key, value in hour_data.items():
            # 키 형식 확인: "0,1" 또는 다른 형식
            if isinstance(key, str) and ',' in key:
                try:
                    parts = key.split(',')
                    o = int(parts[0])
                    d = int(parts[1])
                    if 0 <= o < num_regions and 0 <= d < num_regions:
                        hourly_origin_demand[hour, o] += float(value)
                except:
                    continue

# 출력
for hour in range(24):
    print(f"{hour:02d}:00 ", end="")
    row_sum = 0
    for i in range(num_regions):
        val = hourly_origin_demand[hour, i]
        print(f"{val:>7.0f}", end="")
        row_sum += val
    print(f"{row_sum:>10.0f}")

# 총 수요 확인
total_demand = hourly_origin_demand.sum()
print(f"\n총 출발 수요: {total_demand:.0f}명")

if total_demand == 0:
    print("\n⚠️ 경고: 수요 데이터가 비어있습니다!")
    print("JSON 구조를 확인합니다...")
    
    # 상세 디버깅
    print(f"\n첫 번째 시간대 데이터 타입: {type(demand_data[0])}")
    print(f"샘플 키-값 쌍 (처음 20개):")
    if isinstance(demand_data[0], dict):
        for i, (k, v) in enumerate(list(demand_data[0].items())[:20]):
            print(f"  {i}: '{k}' = {v} (key type: {type(k)}, value type: {type(v)})")
else:
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
        if hour >= len(demand_data):
            break
        hour_data = demand_data[hour]
        
        if isinstance(hour_data, dict):
            for key, value in hour_data.items():
                if isinstance(key, str) and ',' in key:
                    try:
                        parts = key.split(',')
                        o = int(parts[0])
                        d = int(parts[1])
                        if 0 <= o < num_regions and 0 <= d < num_regions:
                            hourly_dest_demand[hour, d] += float(value)
                    except:
                        continue

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

    # ========== 4. CSV 저장 ==========
    print("\n" + "=" * 80)
    print("CSV 파일 저장:")
    print("=" * 80)

    with open('saved_files/demand_outbound_hourly.csv', 'w') as f:
        f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + ",Total\n")
        for hour in range(24):
            row_sum = hourly_origin_demand[hour, :].sum()
            f.write(f"{hour:02d}:00,")
            f.write(",".join([f"{hourly_origin_demand[hour, i]:.0f}" for i in range(num_regions)]))
            f.write(f",{row_sum:.0f}\n")
    print("✅ saved_files/demand_outbound_hourly.csv")

    with open('saved_files/demand_inbound_hourly.csv', 'w') as f:
        f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + ",Total\n")
        for hour in range(24):
            row_sum = hourly_dest_demand[hour, :].sum()
            f.write(f"{hour:02d}:00,")
            f.write(",".join([f"{hourly_dest_demand[hour, i]:.0f}" for i in range(num_regions)]))
            f.write(f",{row_sum:.0f}\n")
    print("✅ saved_files/demand_inbound_hourly.csv")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
