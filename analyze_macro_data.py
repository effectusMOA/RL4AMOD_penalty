import json

# NYC Brooklyn 데이터 로드
with open('src/envs/data/macro/scenario_nyc_brooklyn.json', 'r') as f:
    data = json.load(f)

print("=" * 70)
print("Macro 도시 데이터 구조 분석: NYC Brooklyn")
print("=" * 70)

print("\n1. 기본 정보:")
print(f"  - 전체 키: {list(data.keys())}")
print(f"  - 노드 수 (지역 수): {data['number_of_nodes']}")

print("\n2. Edges (엣지/연결):")
if 'edges' in data:
    edges = data['edges']
    print(f"  - 총 엣지 수: {len(edges)}")
    print(f"  - 예시 (처음 5개):")
    for i, edge in enumerate(edges[:5]):
        print(f"    {i+1}. {edge['i']} → {edge['j']}")
    
    # 완전 그래프 확인
    n = data['number_of_nodes']
    expected = n * (n - 1)  # 자기 자신 제외
    print(f"\n  - 완전 그래프 검증:")
    print(f"    예상 엣지 수: {n} × ({n}-1) = {expected}")
    print(f"    실제 엣지 수: {len(edges)}")
    print(f"    완전 그래프? {'✅ Yes' if len(edges) == expected else '❌ No (일부만 연결)'}")

print("\n3. RebTime (재배치 시간):")
rebtime_data = data['rebTime']
print(f"  - 시간대 수: {len(rebtime_data)}")
print(f"  - 첫 번째 시간대 데이터:")
first_hour = rebtime_data[0]
print(f"    키 (OD 쌍): {list(first_hour.keys())[:5]}...")
print(f"    값 예시:")
for key in list(first_hour.keys())[:3]:
    print(f"      {key}: {first_hour[key]}분")

print("\n4. Time (승객 이동 시간):")
time_data = data['time']
print(f"  - 시간대 수: {len(time_data)}")
first_hour_time = time_data[0]
print(f"  - 값 예시:")
for key in list(first_hour_time.keys())[:3]:
    print(f"      {key}: {first_hour_time[key]}분")

print("\n5. Price (요금):")
price_data = data['price']
print(f"  - 시간대 수: {len(price_data)}")
first_hour_price = price_data[0]
print(f"  - 값 예시:")
for key in list(first_hour_price.keys())[:3]:
    print(f"      {key}: ${first_hour_price[key]:.2f}")

print("\n6. Demand (수요):")
demand_data = data['demand']
print(f"  - 시간대 수: {len(demand_data)}")
first_hour_demand = demand_data[0]
print(f"  - 값 예시 (Poisson λ):")
for key in list(first_hour_demand.keys())[:3]:
    print(f"      {key}: {first_hour_demand[key]:.2f}명/시간")

print("\n" + "=" * 70)
print("도시 데이터에서 가져오는 것:")
print("=" * 70)
print("""
✅ 가져오는 것:
  1. 지역 수 (number_of_nodes)
  2. 지역 간 연결 (edges) - 보통 완전 그래프
  3. 재배치 이동 시간 (rebTime[i,j]) - 시간대별
  4. 승객 이동 시간 (time[i,j]) - 시간대별  
  5. 요금 (price[i,j]) - 시간대별
  6. 수요 (demand[i,j]) - Poisson λ, 시간대별

❌ 가져오지 않는 것:
  1. 실제 도로 네트워크
  2. 도로 제한 속도
  3. 교통 신호등
  4. 차선 정보
  5. 실제 경로

→ 모든 값은 "평균" 또는 "집계된" 데이터!
""")

print("=" * 70)
