"""
시간대별/존별 택시 수요 분석 - 올바른 버전
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
demand_list = data['demand']

print(f"\n데이터 구조:")
print(f"  총 데이터 포인트: {len(demand_list):,}개")
print(f"  예상: {num_regions} 지역 × {num_regions} OD × 1440분 = {8*8*1440:,}개")

# ========== 1. 데이터 파싱 ==========
print(f"\n데이터 파싱 중...")

# 시간대별(hour), origin별 수요 집계
hourly_origin_demand = np.zeros((24, num_regions))
hourly_dest_demand = np.zeros((24, num_regions))

# 각 데이터 포인트 처리
for item in demand_list:
    time_stamp = item['time_stamp']  # 분 단위
    origin = item['origin']
    destination = item['destination']
    demand = item['demand']
    
    # 시간으로 변환 (분 → 시간)
    hour = time_stamp // 60
    
    # 24시간 범위 내에서만
    if 0 <= hour < 24 and 0 <= origin < num_regions and 0 <= destination < num_regions:
        hourly_origin_demand[hour, origin] += demand
        hourly_dest_demand[hour, destination] += demand

# ========== 2. 출발 수요 출력 ==========
print("\n" + "=" * 80)
print("시간대별 각 존의 출발 수요 (Outbound):")
print("=" * 80)
print("시간  ", end="")
for i in range(num_regions):
    print(f"R{i:>7}", end="")
print(f"{'총계':>10}")
print("-" * 80)

for hour in range(24):
    print(f"{hour:02d}:00 ", end="")
    row_sum = 0
    for i in range(num_regions):
        val = hourly_origin_demand[hour, i]
        print(f"{val:>7.0f}", end="")
        row_sum += val
    print(f"{row_sum:>10.0f}")

total_demand = hourly_origin_demand.sum()
print(f"\n일일 총 출발 수요: {total_demand:,.0f}명")

# ========== 3. 도착 수요 출력 ==========
print("\n" + "=" * 80)
print("시간대별 각 존의 도착 수요 (Inbound):")
print("=" * 80)
print("시간  ", end="")
for i in range(num_regions):
    print(f"R{i:>7}", end="")
print(f"{'총계':>10}")
print("-" * 80)

for hour in range(24):
    print(f"{hour:02d}:00 ", end="")
    row_sum = 0
    for i in range(num_regions):
        val = hourly_dest_demand[hour, i]
        print(f"{val:>7.0f}", end="")
        row_sum += val
    print(f"{row_sum:>10.0f}")

# ========== 4. 존별 통계 ==========
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
    
    print(f"\n  Region {i}:")
    print(f"    출발: {total_out:>10,.0f}명 (피크: {peak_hour:02d}:00 - {peak_value:,.0f}명)")
    print(f"    도착: {total_in:>10,.0f}명")
    print(f"    Net:  {net_flow:>10,.0f}명 {'(유입)' if net_flow > 0 else '(유출)'}")

# ========== 5. 대표 시간대 OD Matrix ==========
print("\n" + "=" * 80)
print("대표 시간대 OD Matrix (상위 5개 경로):")
print("=" * 80)

peak_hours = [7, 12, 17]  # 출근, 점심, 퇴근

for peak_hour in peak_hours:
    print(f"\n{peak_hour:02d}:00 시:")
    
    # 해당 시간대 OD 수요 추출
    hour_od_demand = []
    for item in demand_list:
        if item['time_stamp'] // 60 == peak_hour:
            o = item['origin']
            d = item['destination']
            demand = item['demand']
            if o != d and demand > 0:  # 자기 자신 제외
                hour_od_demand.append((o, d, demand))
    
    # 수요 많은 순 정렬
    hour_od_demand.sort(key=lambda x: x[2], reverse=True)
    
    # 상위 10개 표시
    print("  상위 10개 OD:")
    for rank, (o, d, demand) in enumerate(hour_od_demand[:10], 1):
        print(f"    {rank:2}. Region {o} → Region {d}: {demand:>8.0f}명")

# ========== 6. CSV 저장 ==========
print("\n" + "=" * 80)
print("CSV 파일 저장:")
print("=" * 80)

# 출발 수요
with open('saved_files/demand_outbound_hourly.csv', 'w', encoding='utf-8') as f:
    f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + ",Total\n")
    for hour in range(24):
        row_sum = hourly_origin_demand[hour, :].sum()
        f.write(f"{hour:02d}:00,")
        f.write(",".join([f"{hourly_origin_demand[hour, i]:.0f}" for i in range(num_regions)]))
        f.write(f",{row_sum:.0f}\n")
print("✅ saved_files/demand_outbound_hourly.csv")

# 도착 수요
with open('saved_files/demand_inbound_hourly.csv', 'w', encoding='utf-8') as f:
    f.write("Hour," + ",".join([f"Region_{i}" for i in range(num_regions)]) + ",Total\n")
    for hour in range(24):
        row_sum = hourly_dest_demand[hour, :].sum()
        f.write(f"{hour:02d}:00,")
        f.write(",".join([f"{hourly_dest_demand[hour, i]:.0f}" for i in range(num_regions)]))
        f.write(f",{row_sum:.0f}\n")
print("✅ saved_files/demand_inbound_hourly.csv")

# 통계 요약
with open('saved_files/demand_summary.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("Luxembourg 택시 수요 통계 요약\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"일일 총 수요: {total_demand:,.0f}명\n\n")
    
    f.write("존별 일일 총 수요:\n")
    for i in range(num_regions):
        total_out = hourly_origin_demand[:, i].sum()
        total_in = hourly_dest_demand[:, i].sum()
        net_flow = total_in - total_out
        peak_hour = np.argmax(hourly_origin_demand[:, i])
        peak_value = hourly_origin_demand[peak_hour, i]
        
        f.write(f"\n  Region {i}:\n")
        f.write(f"    출발: {total_out:>10,.0f}명 (피크: {peak_hour:02d}:00 - {peak_value:,.0f}명)\n")
        f.write(f"    도착: {total_in:>10,.0f}명\n")
        f.write(f"    Net:  {net_flow:>10,.0f}명 {'(유입)' if net_flow > 0 else '(유출)'}\n")
    
    f.write("\n" + "=" * 80 + "\n")

print("✅ saved_files/demand_summary.txt")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
