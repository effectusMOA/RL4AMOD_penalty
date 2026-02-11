# 3. Method

![Figure 1: Comparison of Rebalancing Frameworks](/C:/Users/Administrator2/.gemini/antigravity/brain/21271faf-2a9f-484d-8886-93a9cc42e18b/uploaded_media_1770782272031.png)
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
