"""
5시간 SUMO 시뮬레이션을 위한 적정 택시 수 계산
"""

# 시간대별 대략적 수요 (Luxembourg)
hourly_demand = {
    6: 1788,   # 06:00
    7: 2870,   # 07:00 (피크)
    8: 3200,   # 08:00 (최대 피크)
    9: 2800,   # 09:00
    10: 2000,  # 10:00
    11: 1800,  # 11:00
}

# 계산 파라미터
avg_trip_duration = 10  # 평균 10분
service_rate = 60 / avg_trip_duration  # 시간당 6회 서비스 가능
safety_factor = 1.2  # 20% 여유

print("=" * 70)
print("Luxembourg SUMO 시뮬레이션 - 적정 택시 수 계산")
print("=" * 70)

print("\n시간대별 권장 택시 수 (8개 지역):")
print("-" * 70)
print(f"{'시간':<10} {'수요(명/h)':<15} {'필요 택시':<15} {'지역당':<15}")
print("-" * 70)

recommendations = {}
for hour, demand in hourly_demand.items():
    required_taxis = int((demand / service_rate) * safety_factor)
    per_region = required_taxis // 8
    recommendations[hour] = {'total': required_taxis, 'per_region': per_region}
    print(f"{hour:02d}:00     {demand:<15} {required_taxis:<15} {per_region:<15}")

print("\n" + "=" * 70)
print("5시간 시뮬레이션 권장 설정 (06:00-11:00)")
print("=" * 70)

# 평균 계산
avg_demand = sum(hourly_demand.values()) / len(hourly_demand)
avg_required = int((avg_demand / service_rate) * safety_factor)
avg_per_region = avg_required // 8

print(f"\n평균 시간당 수요: {avg_demand:.0f}명")
print(f"평균 필요 택시: {avg_required}대")
print(f"지역당 평균: {avg_per_region}대")

# 최대 피크 대비
max_demand = max(hourly_demand.values())
max_required = int((max_demand / service_rate) * safety_factor)
max_per_region = max_required // 8

print(f"\n최대 피크 시 수요: {max_demand}명")
print(f"최대 필요 택시: {max_required}대")
print(f"지역당 최대: {max_per_region}대")

print("\n" + "=" * 70)
print("🎯 권장 설정")
print("=" * 70)

# 보수적 접근
conservative = avg_per_region
moderate = int((avg_per_region + max_per_region) / 2)
aggressive = max_per_region

print(f"""
1. 보수적 (평균 기준):
   acc_init={conservative}  # 총 {conservative * 8}대
   demand_ratio=0.8
   → 안정성: ⭐⭐⭐⭐⭐
   → 피크 시 일부 수요 미충족

2. 적정 (평균+피크 중간):
   acc_init={moderate}  # 총 {moderate * 8}대
   demand_ratio=0.8
   → 안정성: ⭐⭐⭐⭐
   → 균형잡힌 서비스

3. 공격적 (피크 기준):
   acc_init={aggressive}  # 총 {aggressive * 8}대
   demand_ratio=0.7
   → 안정성: ⭐⭐⭐
   → 최대 서비스, 비피크 시 과잉

추천: 옵션 2 (acc_init={moderate})
""")

print("=" * 70)
print("예상 차량 누적 (5시간)")
print("=" * 70)

# 배경 차량 + 택시 추정
background_base = 5000  # 06:00 기준 배경 차량
background_growth = 2000  # 시간당 증가
taxis = moderate * 8

for i, hour in enumerate([6, 7, 8, 9, 10, 11]):
    total_bg = background_base + (i * background_growth)
    total_vehicles = total_bg + taxis
    buf_estimate = int(total_vehicles * 0.3)  # 30% 버퍼 가정
    
    print(f"{hour:02d}:00 - 배경: {total_bg:5d} + 택시: {taxis:3d} = 총: {total_vehicles:5d} (BUF ~{buf_estimate:5d})")

print("\n최대 예상 차량: ~17,000-20,000대")
print("→ SUMO 한계: ~30,000-40,000대")
print("→ 여유 충분 ✅")

print("\n" + "=" * 70)
