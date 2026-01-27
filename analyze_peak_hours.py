import json
import numpy as np
from collections import defaultdict

# JSON 파일 로드
with open('src/envs/data/scenario_lux8.json', 'r') as f:
    data = json.load(f)

# 시간대별 수요 집계
hourly_demand = defaultdict(float)
hourly_count = defaultdict(int)

for entry in data['demand']:
    time_stamp = entry['time_stamp']  # 분 단위 (0-1439)
    hour = time_stamp // 60  # 시간 단위 (0-23)
    demand = entry['demand']
    
    hourly_demand[hour] += demand
    hourly_count[hour] += 1

# 시간당 평균 수요 계산
print("=" * 70)
print("룩셈부르크 택시 수요 분석 (scenario_lux8.json)")
print("=" * 70)
print(f"\n{'시간대':<10} {'총 수요':<15} {'OD쌍 수':<12} {'평균 수요':<12} {'수요 레벨':<15}")
print("-" * 70)

# 시간대별 출력
total_demand = 0
peak_hours = []
for hour in range(24):
    total = hourly_demand[hour]
    count = hourly_count[hour]
    avg = total / count if count > 0 else 0
    total_demand += total
    
    # 수요 레벨 분류
    if avg > 0.5:
        level = "🔴 매우 높음"
        peak_hours.append((hour, total))
    elif avg > 0.3:
        level = "🟠 높음"
        peak_hours.append((hour, total))
    elif avg > 0.15:
        level = "🟡 중간"
    elif avg > 0.05:
        level = "🟢 낮음"
    else:
        level = "⚪ 매우 낮음"
    
    print(f"{hour:02d}:00-{hour:02d}:59  {total:>12.1f}  {count:>10}  {avg:>10.3f}  {level}")

# 피크 타임 식별
peak_hours_sorted = sorted(peak_hours, key=lambda x: x[1], reverse=True)

print("\n" + "=" * 70)
print("피크 타임 분석")
print("=" * 70)

# 오전 피크 (6-12시)
morning_peak = [h for h, d in peak_hours if 6 <= h <= 12]
if morning_peak:
    print(f"\n🌅 오전 피크: {min(morning_peak):02d}:00 - {max(morning_peak):02d}:59")
    morning_demand = sum(d for h, d in peak_hours if 6 <= h <= 12)
    print(f"   총 수요: {morning_demand:.1f}")

# 오후 피크 (12-20시)
afternoon_peak = [h for h, d in peak_hours if 12 <= h <= 20]
if afternoon_peak:
    print(f"\n🌆 오후 피크: {min(afternoon_peak):02d}:00 - {max(afternoon_peak):02d}:59")
    afternoon_demand = sum(d for h, d in peak_hours if 12 <= h <= 20)
    print(f"   총 수요: {afternoon_demand:.1f}")

# 전체 통계
print("\n" + "=" * 70)
print("전체 통계")
print("=" * 70)
print(f"24시간 총 수요: {total_demand:.1f}")
print(f"시간당 평균 수요: {total_demand/24:.1f}")
print(f"분당 평균 수요: {total_demand/24/60:.2f}")

# 피크 vs 비피크
peak_total = sum(d for h, d in peak_hours)
print(f"\n피크 시간대 총 수요: {peak_total:.1f} ({peak_total/total_demand*100:.1f}%)")
print(f"비피크 시간대 총 수요: {total_demand - peak_total:.1f} ({(total_demand-peak_total)/total_demand*100:.1f}%)")

# 택시 수 권장
print("\n" + "=" * 70)
print("권장 택시 수 (8개 지역)")
print("=" * 70)

for hour in range(24):
    total = hourly_demand[hour]
    count = hourly_count[hour]
    avg = total / count if count > 0 else 0
    
    # 시간당 수요를 택시 수로 변환 (대략적 계산)
    # 가정: 1대 택시가 시간당 4번 운행 가능
    # 필요 택시 = 시간당 수요 / 4
    recommended_taxis = int(total / 4 * 1.2)  # 1.2 = 안전계수
    per_region = recommended_taxis // 8
    
    if avg > 0.3:  # 높은 수요 시간대만 출력
        print(f"{hour:02d}:00-{hour:02d}:59  총 {recommended_taxis:>4}대 (지역당 ~{per_region:>3}대)")

# 권장 설정
print("\n" + "=" * 70)
print("🎯 권장 학습 설정")
print("=" * 70)

if morning_peak and afternoon_peak:
    all_peak = morning_peak + afternoon_peak
    print(f"\n✅ 피크 시간대 전체 학습:")
    print(f"   time_start={min(all_peak)}")
    print(f"   duration={max(all_peak) - min(all_peak) + 1}")
    print(f"   acc_init=80-100")
    
if morning_peak:
    print(f"\n✅ 오전 피크만 학습:")
    print(f"   time_start={min(morning_peak)}")
    print(f"   duration={max(morning_peak) - min(morning_peak) + 1}")
    print(f"   acc_init=70-90")

if afternoon_peak:
    print(f"\n✅ 오후 피크만 학습:")
    print(f"   time_start={min(afternoon_peak)}")
    print(f"   duration={max(afternoon_peak) - min(afternoon_peak) + 1}")
    print(f"   acc_init=80-100")

print("\n✅ 24시간 전체 학습 (비권장):")
print(f"   time_start=0")
print(f"   duration=24")
print(f"   acc_init=40-50 (야간 과잉 방지)")

print("\n" + "=" * 70)
