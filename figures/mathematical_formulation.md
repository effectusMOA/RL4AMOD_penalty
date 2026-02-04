# Rebalancing 최적화 수식 정식화

## 1. 문제 정의 (Problem Definitions)

도로 네트워크를 그래프 $G = (V, E)$로 정의합니다. 여기서 $V$는 지역(노드)의 집합, $E$는 간선(도로 연결)의 집합입니다.

**파라미터 (Parameters):**
- $v_i$: 시간 $t$에 지역 $i$에 있는 현재 가용 차량 수.
- $v_i^d$: 시간 $t+1$에 지역 $i$에서 필요한 목표 차량 수 (Policy Network에 의해 결정됨).
- $c_{ij}$: 지역 $i$에서 지역 $j$로 재분배(Rebalancing)하는 비용 (예: 이동 시간 또는 거리).
- $\lambda$: 부족분 페널티 계수 (Soft SAC의 제어 파라미터).

**결정 변수 (Decision Variables):**
- $x_{ij} \in \mathbb{Z}_{\ge 0}$: 지역 $i$에서 지역 $j$로 재분배되는 차량의 수.
- $s_i \in \mathbb{R}_{\ge 0}$: 지역 $i$의 차량 부족분(Shortage)을 나타내는 Slack 변수 (Soft SAC에서만 사용).

---

## 2. Hard SAC (Hard Constraint LP)

Hard SAC 방식은 재분배 비용과 상관없이 목표 차량 분포를 **반드시** 충족하도록 강제합니다. 이는 종종 과도한 장거리 공차 운행을 초래합니다.

### 목적 함수 (Objective Function)
총 재분배 비용을 최소화합니다:
$$\min \sum_{(i,j) \in E} c_{ij} x_{ij}$$

### 제약 조건 (Constraints)
1.  **유량 보존 (Flow Conservation - 엄격함)**: 각 노드의 순유입량(Net Inflow)은 부족분을 충족해야 합니다.
   $$\sum_{j:(j,i) \in E} x_{ji} - \sum_{j:(i,j) \in E} x_{ij} \ge v_i^d - v_i, \quad \forall i \in V$$
    *해석*: 만약 노드에 차량이 더 필요하다면($v_i^d > v_i$), 순유입량은 최소한 그 부족분만큼 되어야 합니다. 이미 차량이 충분하다면 이 제약은 자연스럽게 만족됩니다.

2.  **용량 제약 (Capacity Constraint)**: 노드를 떠나는 재분배 차량 수는 현재 보유한 차량 수를 초과할 수 없습니다.
   $$\sum_{j:(i,j) \in E} x_{ij} \le v_i, \quad \forall i \in V$$

3.  **비음 제약 (Non-negativity)**:
   $$x_{ij} \ge 0$$

---

## 3. Soft SAC (Soft Constraint LP with Penalty)

Soft SAC 방식은 Slack 변수 $s_i$를 도입하여 엄격한 유량 보존 제약을 완화합니다. 이를 통해 비용이 너무 높을 경우 목표 분포를 완벽히 맞추지 않는 것을 허용합니다.

### 목적 함수 (Objective Function)
재분배 비용과 부족분 페널티의 가중 합을 최소화합니다:
$$\min \left( \sum_{(i,j) \in E} c_{ij} x_{ij} + \lambda \sum_{i \in V} s_i \right)$$

### 제약 조건 (Constraints)
1.  **유량 보존 (Flow Conservation - 완화됨)**:
   $$\sum_{j:(j,i) \in E} x_{ji} - \sum_{j:(i,j) \in E} x_{ij} + s_i \ge v_i^d - v_i, \quad \forall i \in V$$
    *해석*: 순유입량에 부족분($s_i$)을 더한 값이 목표 부족분을 커버해야 합니다. 재분배 비용이 너무 비싸다면, 솔버는 $x_{ji}$를 늘리는 대신 $s_i$를 늘리는 선택을 할 수 있습니다.

2.  **용량 제약 (Capacity Constraint)** (Hard SAC와 동일):
   $$\sum_{j:(i,j) \in E} x_{ij} \le v_i, \quad \forall i \in V$$

3.  **비음 제약 (Non-negativity)**:
   $$x_{ij} \ge 0, \quad s_i \ge 0$$

---

## 4. Slack ($s_i$)과 페널티 ($\lambda$)의 이해

### Slack ($s_i$)이란 무엇인가?
Slack 변수 $s_i$는 지역 $i$에서 **충족되지 못한 차량 수요(Shortage)**를 의미합니다. 즉, 목표 차량 수에 도달하지 못한 부족분입니다.
$$s_i = \max \left( 0, (v_i^d - v_i) - (\text{순 재분배 유입량}) \right)$$

**예시 시나리오:**
- **현재 상황 ($v_i$)**: Zone A에 택시 5대 있음.
- **목표 ($v_i^d$)**: Policy가 Zone A에 택시 10대를 요구함.
- **필요량**: 5대를 외부에서 가져와야 함.

1. **Hard SAC**: 무조건 5대를 가져옴. $\rightarrow$ $s_i=0$. (비용이 매우 비쌀 수 있음)
2. **Soft SAC**: 비용이 너무 비싸서 3대만 가져오기로 결정함.
   - 확보 차량: $5 + 3 = 8$대.
   - **부족분 ($s_i$): $10 - 8 = 2$대.** (이 2대에 대해 페널티 지불)

### 페널티 계수 ($\lambda$)의 역할
파라미터 $\lambda$는 **운영 효율성** (낮은 재분배 비용)과 **서비스 품질** (목표 분포 충족) 사이의 **Trade-off**를 조절합니다.

-   **높은 $\lambda$ (예: $\lambda \to \infty$)**:
    -   페널티 비용 $\lambda s_i$가 매우 커집니다.
    -   솔버는 $s_i$를 0으로 만들기 위해 비용을 감수하고 재분배를 수행합니다.
    -   **결과**: **Hard SAC**와 동일한 동작 (목표 충족을 위해 최대 재분배).
    
-   **낮은 $\lambda$ (예: $\lambda \approx 0$)**:
    -   페널티 비용이 무시할 수준입니다.
    -   솔버는 재분배 비용($\sum c_{ij} x_{ij}$) 최소화에 집중합니다.
    -   재분배를 거의 하지 않고($x_{ij}=0$) 높은 부족분($s_i > 0$)을 감수할 수 있습니다.
    -   **결과**: 공차 운행은 최소화되지만, 서비스 가용성이 떨어질 수 있음.

-   **최적의 $\lambda$ (예: $\lambda \approx 5$)**:
    -   두 목표 사이의 균형을 맞춥니다.
    -   재분배 비용 $c_{ij}$가 미충족 페널티보다 저렴할 때만 재분배를 수행합니다.
    -   즉, "비용 효율적인" 재분배만 수행하고, 비효율적인 장거리 재분배는 포기합니다.

---

## 5. Baseline Models Formulation

본 연구에서 비교 대상으로 사용된 Baseline 모델들의 수학적 정식화는 다음과 같습니다.

### 5.1. No Rebalancing
가장 기본적인 형태로, 어떠한 재분배도 수행하지 않습니다.
$$x_{ij} = 0, \quad \forall (i, j) \in E$$
- **목적**: 시스템의 자연스러운 차량 흐름만을 이용할 때의 하한선(Lower Bound) 성능을 측정합니다.

### 5.2. Heuristic (Equal Distribution)
모든 지역의 차량 수를 균등하게 맞추는 것을 목표로 합니다.
- **목표 차량 수 ($v_i^d$)**: $\frac{\sum_{k \in V} v_k}{|V|}$
- **최적화 문제**:
  재분배 비용을 최소화하면서 목표 분포를 달성합니다. (Hard Constraint 적용) (This experiment used PuLP to enforce strict constraints).
  
  **목적 함수**:
 $$\min \sum_{(i,j) \in E} c_{ij} x_{ij}$$
  
  **제약 조건**:
 $$\sum_{j:(j,i) \in E} x_{ji} - \sum_{j:(i,j) \in E} x_{ij} \ge v_i^d - v_i, \quad \forall i \in V$$
 $$\sum_{j:(i,j) \in E} x_{ij} \le v_i, \quad \forall i \in V$$

### 5.3. MPC (Model Predictive Control)
미래의 수요와 차량 흐름을 예측하여 유한한 시간 지평(Time Horizon, $T$) 동안의 총 이익을 최대화합니다.

**목적 함수 (Objective Function)**:
$$\max \sum_{t=t_0}^{t_0+T-1} \left( \sum_{e \in E_{demand}} y_{e,t} \cdot p_e - \beta \left( \sum_{e \in E} x_{e,t}^{reb} \cdot \tau_e + \sum_{e \in E_{demand}} y_{e,t} \cdot \tau_{e} \right) \right)$$

여기서:
- $y_{e,t}$: 시간 $t$에 간선 $e$의 승객 수요 처리량
- $x_{e,t}^{reb}$: 시간 $t$에 간선 $e$의 재분배 유량
- $p_e$: 승객 요금 (Price)
- $\tau_e$: 이동 시간 (Travel Time) / 비용
- $\beta$: 비용 가중치

**제약 조건 (Constraints)**:
1.  **차량 흐름 보존 (Flow Dynamics)**:
   $$acc_{i, t+1} = acc_{i, t} - \text{Outflow}_{i,t} + \text{Inflow}_{i,t}$$
2.  **용량 제약 (Capacity)**:
   $$\sum \text{Outflow}_{i,t} \le acc_{i, t}$$
3.  **수요 제약 (Demand)**:
   $$y_{e,t} \le \text{Demand}_{e,t}$$
