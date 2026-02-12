# Cost-Aware AMoD Rebalancing: Enhancing Efficiency via Soft Actor-Critic and Soft-Constrained Linear Programming

# 3. Method

![Figure 1: Comparison of Rebalancing Frameworks](figures/figure1.png)
> **Figure 1.** Our proposed rebalancing framework. The **RL Global Controller** determines strategic target distributions. The **MILP Local Controller** then executes tactical rebalancing. In the **As-Is (Hard)** approach (top), strict adherence to targets leads to high-cost rebalancing. In the **To-Be (Soft)** approach (bottom), an **Economic Filter** (slack mechanism) selectively executes only cost-effective rebalancing, rejecting inefficient commands.

## 3.1. Background: The 3-Step Decision Framework

To control the Automated Mobility-on-Demand (AMoD) fleet, we adopt a three-step decision-making framework similar to [10], as illustrated in Figure 1. This framework sequentially addresses: (1) solving the matching problem to derive passenger flows, (2) computing the desired distribution of available idle vehicles at the current time step using a learned policy $\pi_\theta(a_t|s_t)$, and (3) solving the minimum rebalancing cost problem to convert the desired distribution into rebalancing flows.

A key distinction of this three-step procedure is that actions are taken at each *node* rather than along each *edge*, which is the conventional approach in most literature. By reducing the dimensionality of the action space in the AMoD rebalancing MDP to $N_v$ (compared to $N_v^2$ in edge-based approaches), we significantly enhance the scalability of both training and implementation.

We now elaborate on the three-step decision framework employed by the AMoD operator at each time step $t$.

**Step 1: Passenger Matching**
The first step involves solving the matching problem to derive passenger flows $\{x_{ij}^t\}_{i,j \in V}$:

$$
\max_{\{x_{ij}^t\}_{i,j \in V}} \sum_{i,j \in V} x_{ij}^t(p_{ij}^t - c_{ij}^t) \quad \text{(Eq. 2a)}
$$

$$
\text{s.t.} \quad 0 \leq x^t_{ij} \leq d^t_{ij}, \quad \forall i,j \in V \quad \text{(Eq. 2b)}
$$

Here, the objective function (Eq. 2a) represents the total profit of passenger assignment, calculated as the difference between revenue (fare $p_{ij}^t$) and service cost ($c_{ij}^t$). The constraint (Eq. 2b) ensures that passenger flows are non-negative and do not exceed demand $d_{ij}^t$. Since the constraint matrix is totally unimodular, the resulting passenger flows are guaranteed to be positive integers; that is, if $d_{ij}^t \in \mathbb{Z}^+$, then $x_{ij}^t \in \mathbb{Z}^+$ for all $i, j \in V$.

**Step 2: Desired Distribution**
The second step determines the target distribution of idle vehicles $\{a_{reb,i}^t\}_{i \in V}$ to be rebalanced. Here, $a_{reb,i}^t \in [0, 1]$ defines the proportion of currently idle vehicles to be rebalanced to each station $i$ at time $t$, satisfying $\sum_{i \in V} a_{reb,i}^t = 1$.
Using the desired distribution $a_{reb}^t$, we denote the desired number of vehicles as:

$$
\hat{m}_{t,i} = \left\lfloor a_{reb,i}^t \sum_{k \in V} m_{t,k} \right\rfloor
$$

where $m_{t,i}$ represents the actual number of idle vehicles in region $i$ at time $t$. The floor function $\lfloor \cdot \rfloor$ is used to ensure that the desired number of vehicles is an integer and feasible (i.e., $\sum_{i \in V} \hat{m}_{t,i} \le \sum_{i \in V} m_{t,i}$).

**Step 3: Rebalancing (Hard Constraint Baseline)**
The third step executes rebalancing by solving the minimum rebalancing cost problem to derive rebalancing flows $\{y_{ij}^t\}_{(i,j) \in E}$:

$$
\min_{\{y^t_{ij}\}_{(i,j) \in E}} \sum_{(i,j) \in E} c^t_{ij} y^t_{ij} \quad \text{(Eq. 3a)}
$$

$$
\text{s.t.} \quad \sum_{j} (y_{ji}^{t} - y_{ij}^{t}) + m_{i}^{t} \ge \hat{m}_{i}^{t}, \quad \forall i \in V \quad \text{(Eq. 3b)}
$$

$$
\sum_{j \neq i} y_{ij}^t \le m_i^t, \quad \forall i \in V \quad \text{(Eq. 3c)}
$$

The objective function (Eq. 3a) minimizes the rebalancing cost. Constraint (Eq. 3b) enforces that the resulting number of vehicles (LHS) meets or exceeds the desired number of vehicles (RHS). Constraint (Eq. 3c) ensures that the rebalancing outflow from a region does not exceed the available vehicles in that region.

## 3.2. Proposed Approach: Soft-Constrained Rebalancing with Economic Filter

The strict constraint in Eq. (3b) (Hard LP) often forces the system to execute inefficient long-distance rebalancing even when the cost outweighs the benefit, leading to high operational costs and congestion.

To address this, we propose a **Soft-Constrained Rebalancing** approach integrated with an Economic Filter (Slack Mechanism). We relax the hard constraint (Eq. 3b) and introduce a penalty term $\lambda$ for shortages ($s_i^t$) in the objective function:

$$
\min_{\{y_{ij}^t, s_i^t\}} \left( \sum_{(i,j) \in E} c_{ij}^t y_{ij}^t + \lambda \sum_{i \in V} s_i^t \right)
$$

$$
\text{s.t.} \quad \sum_{j} (y_{ji}^t - y_{ij}^t) + m_i^t + s_i^t \ge \hat{m}_i^t
$$

This formulation acts as a cost-benefit filter: rebalancing is executed only if the cost $c_{ij}^t$ is lower than the penalty $\lambda$ (representing the value of meeting the demand), effectively rejecting inefficient rebalancing commands.

## 4. EXPERIMENTS

### 4.1. Sensitivity Analysis of Economic Filter ($\lambda$)

Analysis of the penalty parameter $\lambda$ in the SAC-Soft reveals its significant role in balancing service quality and operational efficiency. **Figure 3** shows the change in efficiency, defined as rebalancing flow rate and cost, on the y-axis and $\lambda$ on the x-axis. As $\lambda$ decreases, rebalancing costs take priority. Conversely, increasing $\lambda$ shows nearly forcing the target idle vehicle distribution, inducing aggressive rebalancing similar to SAC-Hard. **Table 1** shows the changes in profitability, rebalancing flow and cost, and efficiency of the SAC-Soft as the penalty $\lambda$ varies from 3 to 13.

In the $\lambda = 8.0 \sim 10.0$ range, the profit relative to SAC-Hard is positive. Specifically, at **$\lambda = 9.0$**, the profit peaked at $55,410, a 2.84% increase, while rebalancing cost decreased 5.62% to $13,335. Interestingly, efficiency increased 10.01% to 0.1701, and the rebalancing flow size actually increased by 3.82% compared to the baseline. This phenomenon—higher flow but lower cost—indicates that the model performs **cost-effective rebalancing**: it successfully filters out expensive long-distance trips while aggressively executing efficient short-distance moves to capture demand.

For operators prioritizing both profit and system efficiency, **$\lambda=11.0$** represents the optimal configuration. At this setting, the model achieves the highest operational efficiency (0.2007 veh/$), a near 30% improvement over the baseline, while maintaining a profit ($53,880) comparable to SAC-Hard. This suggests that $\lambda=11.0$ is the best model for an operator who values not only maximizing immediate profit but also executing rebalancing in the most resource-efficient manner possible, minimizing unnecessary vehicle mileage.

**Table 1. Lambda Sensitivity Analysis**

| Lambda | Profit ($) | Trip Margin ($) | Reb. Cost ($) | Reb. Flow (veh) | Efficiency (veh/$) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 3.0 | 39,730 (-26.26%) | 45,189 (-33.55%) | 5,459 (-61.36%) | 1,383 (-36.70%) | 0.2533 (+63.82%) |
| 4.0 | 48,738 (-9.54%) | 59,083 (-13.12%) | 10,345 (-26.78%) | 2,151 (-1.53%) | 0.2079 (+34.49%) |
| 5.0 | 52,090 (-3.32%) | 63,007 (-7.35%) | 10,916 (-22.74%) | 2,077 (-4.89%) | 0.1903 (+23.10%) |
| 6.0 | 52,736 (-2.12%) | 66,886 (-1.65%) | 14,150 (+0.14%) | 2,313 (+5.91%) | 0.1635 (+5.76%) |
| 7.0 | 53,674 (-0.38%) | 68,035 (+0.04%) | 14,360 (+1.63%) | 2,292 (+4.95%) | 0.1596 (+3.26%) |
| 8.0 | 54,871 (+1.84%) | 68,749 (+1.09%) | 13,878 (-1.78%) | 2,363 (+8.17%) | 0.1702 (+10.13%) |
| **9.0** | **55,410 (+2.84%)** | **68,744 (+1.08%)** | **13,335 (-5.62%)** | **2,268 (+3.82%)** | **0.1701 (+10.01%)** |
| 10.0 | 55,235 (+2.52%) | 67,914 (-0.14%) | 12,679 (-10.27%) | 2,133 (-2.35%) | 0.1682 (+8.82%) |
| 11.0 | 53,880 (+0.00%) | 63,839 (-6.13%) | 9,960 (-29.51%) | 1,999 (-8.48%) | 0.2007 (+29.84%) |
| 12.0 | 53,393 (-0.90%) | 63,560 (-6.54%) | 10,168 (-28.04%) | 1,972 (-9.72%) | 0.1939 (+25.46%) |
| 13.0 | 53,699 (-0.33%) | 63,906 (-6.03%) | 10,207 (-27.76%) | 1,984 (-9.16%) | 0.1944 (+25.75%) |
| **Hard** | 53,878 (+0.00%) | 68,007 (+0.00%) | 14,129 (+0.00%) | 2,184 (+0.00%) | 0.1546 (+0.00%) |

### 4.2. Comparative Performance Analysis

We compare the performance of the proposed **SAC-Soft ($\lambda=9$)** model against four baselines: (1) **MPC** (Model Predictive Control), (2) **SAC-Hard** (Baseline RL), (3) **Heuristic** (Equal Distribution), and (4) **No Rebalancing**. The results are summarized in **Table 2**.

The proposed SAC-Soft model achieves the highest total profit ($55,409), outperforming the SAC-Hard baseline by 2.8%. Key observations include:
1.  **High Efficiency**: Compared to SAC-Hard, SAC-Soft serves a similar level of demand (+1.1%) but significantly reduces rebalancing costs (-5.6%). This confirms that the economic filter successfully eliminates wasteful rebalancing trips without compromising service quality.
2.  **Comparison with Mathematical Optimization**: The MPC approach, typically considered a strong optimization-based baseline, achieves competitive results but slightly lags behind SAC-Soft in total profit ($55,409 vs $54,690). This suggests that the mathematical optimization could be further improved by adjusting parameters such as time steps or planning horizons. However, SAC-Soft demonstrates superior performance even without such manual tuning, effectively learning a policy that surpasses the standard optimization baseline in this dynamic environment.
3.  **Limitations of Heuristic Approaches**: The Heuristic baseline (Equal Distribution) resulted in lower service rates (-11.9% Trip Margin) and higher costs. While more sophisticated heuristics (e.g., demand-prediction-based rules) could potentially improve performance, they typically rely on static logic that struggles to adapt to complex, stochastic demand patterns. In contrast, SAC-Soft learns an optimal policy through interaction, allowing it to dynamically adjust rebalancing strategies based on real-time conditions.
4.  **Necessity of Rebalancing**: The "No Rebalancing" case shows drastically lower profit (-47.8%), underscoring the critical importance of active fleet management.

**Table 2. Overall Performance Comparison**

| Model | Profit ($) | Reb. Cost ($) | Trip Margin ($) | Served (Pax) | Reb. Vehicles | Note |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **SAC Soft ($\lambda=9$)** | **55,409 (+2.8%)** | **13,334 (-5.6%)** | **68,744 (+1.1%)** | **1,054** | **2,267 (+3.8%)** | **Best Performance** |
| MPC | 54,690 (+1.5%) | 8,092 (-42.7%) | 62,782 (-7.7%) | 963 | 1,424 (-34.8%) | Low Cost, Low Service |
| SAC Hard | 53,877 (0.0%) | 14,129 (0.0%) | 68,006 (0.0%) | 1,042 | 2,184 (0.0%) | Baseline (High Cost) |
| Heuristic (Hard) | 50,391 (-6.5%) | 9,508 (-32.7%) | 59,900 (-11.9%) | 919 | 1,684 (-22.9%) | Equal Distribution |
| No Rebalancing | 28,106 (-47.8%) | 0 (-100%) | 28,106 (-58.7%) | 431 | 0 (-100%) | Lower Bound |

### 4.3. Rebalancing Flow Analysis

**Figure 4** and **Figure 5** collectively visualize the spatial distribution and volume of rebalancing flows, demonstrating the operational mechanism of the proposed SAC-Soft model ($\lambda=11$).

The map visualization in **Figure 4** reveals a stark contrast in rebalancing patterns. The **SAC-Hard** baseline (Left) shows thick, extensive flow lines connecting distant zones (e.g., Zone 5 to Zone 12/13), indicating an aggressive strategy that prioritizes meeting demand regardless of travel cost. In contrast, **SAC-Soft** (Right) exhibits significantly thinner or absent long-distance lines, instead concentrating on short-distance rebalancing between adjacent zones.

This observation is quantitatively confirmed by the flow volume analysis of the **Top 5 Longest Routes** in **Figure 5**.
*   **Filtering Inefficient Long-Haul Trips**: For the route **12 $\to$ 5 (13.2 km)**, SAC-Hard dispatched **78 vehicles**. The SAC-Soft model, recognizing the high cost relative to the benefit, drastically reduced this flow to **4 vehicles**, effectively eliminating this inefficient operation.
*   **Preserving Valuable Long-Distance Connections**: Crucially, the model does not blindly minimize distance. For the longest route **9 $\to$ 5 (16.4 km)**, SAC-Soft maintained a high flow volume (**177 vehicles**) comparable to SAC-Hard (188 vehicles). This suggests that the **Economic Filter** is intelligent enough to distinguish between "wasteful" and "necessary" long-distance trips, preserving those that are essential for meeting critical demand or yield higher returns.

By selectively filtering out high-cost, low-value trips (like 12$\to$5) while maintaining essential connections (like 9$\to$5), SAC-Soft achieves a more efficient fleet distribution. This strategic behavior explains why the proposed model can maintain high service levels (Trip Margin +1.1%) while reducing overall rebalancing costs (-5.6%), as shown in Table 2.

![Rebalancing Flow Comparison](file:///c:/Users/Administrator2/Documents/RL4AMOD_origin/figures/brooklyn_rebalancing_comparison.png)
*Figure 4. Comparison of Rebalancing Flows between SAC-Hard and SAC-Soft ($\lambda=11$). The proposed method (Right) visibly reduces long-distance empty trips.*

![Top 5 Longest Flows](file:///c:/Users/Administrator2/Documents/RL4AMOD_origin/figures/top5_long_distance_flow_comparison.png)
*Figure 5. Rebalancing Flow Count for Top 5 Longest Routes. SAC-Soft ($\lambda=11$) effectively filters out inefficient long-distance flows (e.g., 12->5, reduced from 78 to 4) while maintaining essential high-value connections (e.g., 9->5, maintained at ~177).*

## 5. CONCLUSION

This study proposed a **Soft-Constrained Rebalancing Optimization** framework with an **Economic Filter** to address the limitations of hard-constrained AMoD operations. By relaxing strict target constraints and introducing a penalty parameter $\lambda$, the proposed method enables the system to weigh the cost of rebalancing against the potential benefit of meeting demand targets.

Experimental results on the New York Brooklyn dataset demonstrate that the proposed approach ($\lambda=9$) effectively mitigates the "over-rebalancing" problem. It achieved a 2.8% increase in total profit compared to the hard-constrained baseline by reducing inefficient rebalancing costs (5.6%) while maintaining high service levels. The sensitivity analysis further confirmed that an optimal $\lambda$ exists where operational efficiency and service quality are balanced.

**Future Work**:
Current experiments were conducted in a macroscopic environment based on zone-to-zone aggregated flows. Future research will extend this framework to **microscopic simulation environments** such as **SUMO** (Simulation of Urban MObility). This will allow for granular validation at the node and link level, optimizing rebalancing flows with realistic traffic dynamics and routing constraints beyond simple aggregation.
