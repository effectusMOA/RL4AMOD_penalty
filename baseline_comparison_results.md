# Baseline Comparison Analysis

본 문서는 SAC Soft ($\lambda=9$) 모델과 다양한 Baseline 모델들의 성능을 비교 분석한 결과를 보여줍니다.

## 1. 성능 비교 요약 (Performance Summary)

**기준 모델 (Baseline): SAC Hard**
- 모든 변화율(%)은 SAC Hard 모델을 기준으로 계산되었습니다.

| Model | Reward ($) | Rebalancing Cost ($) | Served Demand | Reb. Vehicles | 비고 |
|:---|---:|---:|---:|---:|:---|
| **SAC Soft ($\lambda=9$)** | **55,409** (+2.8%) | **13,334** (-5.6%) | **68,744** (+1.1%) | 2,267 | **Best Performance** |
| MPC | 54,690 (+1.5%) | 8,092 (-42.7%) | 62,782 (-7.7%) | 1,424 | Low Cost, Low Service |
| SAC Hard | 53,877 (0.0%) | 14,129 (0.0%) | 68,006 (0.0%) | 2,184 | Baseline (High Cost) |
| Heuristic (Hard) | 50,391 (-6.5%) | 9,508 (-32.7%) | 59,900 (-11.9%) | 1,684 | Equal Distribution |
| No Rebalancing | 28,106 (-47.8%) | 0 (-100%) | 28,106 (-58.7%) | 0 | Lower Bound |

---

## 2. 상세 분석 (Detailed Analysis)

### 2.1. SAC Soft ($\lambda=9$)의 우수성
- **최고의 수익성 (Reward)**: Hard 모델 대비 **2.8%** 높은 총 보상($55,409)을 달성했습니다.
- **효율적인 재분배**:
    - **Served Demand**는 Hard 모델보다 **1.1% 더 높습니다** ($68,744 vs $68,006). 즉, 더 많은 승객을 태웠습니다.
    - 그럼에도 불구하고 **Rebalancing Cost**는 **5.6% 더 낮습니다** ($13,334 vs $14,129).
    - **결론**: Soft SAC는 불필요한 장거리 공차 운행을 줄이면서도($S_i$ 활용), 핵심적인 수요 지역으로 차량을 효과적으로 보냈음을 의미합니다.

### 2.2. MPC (Model Predictive Control)
- **높은 비용 효율성**: 재분배 비용($8,092)이 매우 낮습니다. 이는 단기적인 최적 경로를 잘 찾는다는 것을 의미합니다.
- **낮은 서비스 품질**: 그러나 Served Demand가 SAC 모델들보다 약 **7~8% 낮습니다**.
- 이는 T=6 (약 18분)이라는 짧은 예측 기간(Horizon) 때문에, 먼 거리에서 발생하는 대량의 미래 수요를 미리 대비하지 못했기 때문으로 분석됩니다.

### 2.3. Heuristic (Equal Distribution)
- **단순함의 한계**: 모든 지역에 차량을 균등하게 배치하려는 전략은 수요 불균형이 심한 NYC 데이터셋에서 효과적이지 않습니다.
- Reward가 SAC 계열보다 약 10% 가까이 낮습니다.

### 2.4. No Rebalancing
- **재분배의 필요성**: 재분배 없이는 수익이 거의 반토막($28,106) 납니다. 이는 AMoD 시스템에서 재분배 알고리즘이 필수적임을 보여줍니다.

---

## 3. 결론 (Conclusion)
**SAC Soft ($\lambda=9$)**는 비용(Cost)과 서비스(Served Demand) 사이의 균형을 가장 잘 맞추며, 기존 Hard LP 방식과 최신 MPC 방식 모두를 능가하는 성능을 보여주었습니다. 특히 Hard LP의 경직된 제약을 완화함으로써 **"더 적은 비용으로 더 많은 승객을 태우는"** 것이 가능함을 입증했습니다.
