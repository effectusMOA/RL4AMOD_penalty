# Rebalancing Optimization Formulation

## 1. Problem Definitions

Let the road network be represented as a graph $G = (V, E)$, where $V$ is the set of regions (nodes) and $E$ is the set of edges (road connections).

**Parameters:**
- $v_i$: Current number of available vehicles in region $i$ at time $t$.
- $v_i^d$: Desired number of vehicles in region $i$ at time $t+1$ (determined by the Policy Network).
- $c_{ij}$: Cost of rebalancing from region $i$ to region $j$ (e.g., travel time or distance).
- $\lambda$: Shortage penalty coefficient (Control parameter for Soft SAC).

**Decision Variables:**
- $x_{ij} \in \mathbb{Z}_{\ge 0}$: Number of vehicles rebalanced from region $i$ to region $j$.
- $s_i \in \mathbb{R}_{\ge 0}$: Slack variable representing the shortage of vehicles in region $i$ (used only in Soft SAC).

---

## 2. Hard SAC (Hard Constraint LP)

The Hard SAC approach strictly enforces the requirement to meet the desired vehicle distribution, regardless of the rebalancing cost. This often leads to excessive long-distance empty trips.

### Objective Function
Minimize the total rebalancing cost:
$$ \min \sum_{(i,j) \in E} c_{ij} x_{ij} $$

### Constraints
1.  **Flow Conservation (Strict)**: The net inflow of vehicles must satisfy the deficit at each node.
    $$ \sum_{j:(j,i) \in E} x_{ji} - \sum_{j:(i,j) \in E} x_{ij} \ge v_i^d - v_i, \quad \forall i \in V $$
    *Interpretation*: If a node needs more vehicles ($v_i^d > v_i$), the net inflow must be at least the deficit. If it has surplus, the constraint is trivially satisfied (since decision variables are non-negative and can be zero).

2.  **Capacity Constraint**: The number of rebalancing vehicles leaving a node cannot exceed the available vehicles.
    $$ \sum_{j:(i,j) \in E} x_{ij} \le v_i, \quad \forall i \in V $$

3.  **Non-negativity**:
    $$ x_{ij} \ge 0 $$

---

## 3. Soft SAC (Soft Constraint LP with Penalty)

The Soft SAC approach relaxes the strict flow conservation constraint by introducing a slack variable $s_i$. This allows the system to deviate from the desired distribution if the cost of satisfying it is too high.

### Objective Function
Minimize the weighted sum of rebalancing cost and shortage penalty:
$$ \min \left( \sum_{(i,j) \in E} c_{ij} x_{ij} + \lambda \sum_{i \in V} s_i \right) $$

### Constraints
1.  **Flow Conservation (Relaxed with Slack)**:
    $$ \sum_{j:(j,i) \in E} x_{ji} - \sum_{j:(i,j) \in E} x_{ij} + s_i \ge v_i^d - v_i, \quad \forall i \in V $$
    *Interpretation*: The net inflow plus the shortage ($s_i$) must cover the deficit. If rebalancing is too expensive, the solver can choose to increase $s_i$ instead of increasing $x_{ji}$.

2.  **Capacity Constraint** (Same as Hard SAC):
    $$ \sum_{j:(i,j) \in E} x_{ij} \le v_i, \quad \forall i \in V $$

3.  **Non-negativity**:
    $$ x_{ij} \ge 0, \quad s_i \ge 0 $$

---

## 4. Understanding Slack ($s_i$) and Penalty ($\lambda$)

### What is Slack ($s_i$)?
The slack variable $s_i$ represents the **unmet demand for vehicles** (shortage) in region $i$.
$$ s_i = \max \left( 0, (v_i^d - v_i) - (\text{Net Rebalancing Inflow}) \right) $$
- If $s_i = 0$: The desired distribution is fully satisfied (Hard constraint met).
- If $s_i > 0$: The region received fewer vehicles than requested.

### Role of Penalty Coefficient ($\lambda$)
The parameter $\lambda$ controls the trade-off between **operational efficiency** (low rebalancing cost) and **service quality** (meeting desired distribution).

-   **High $\lambda$ (e.g., $\lambda \to \infty$)**:
    -   The penalty cost $\lambda s_i$ becomes huge.
    -   The solver is forced to minimize $s_i$ to zero.
    -   **Result**: Converges to **Hard SAC** behavior (maximum rebalancing to meet targets).
    
-   **Low $\lambda$ (e.g., $\lambda \approx 0$)**:
    -   The penalty cost is negligible.
    -   The solver prioritizes minimizing rebalancing cost ($\sum c_{ij} x_{ij}$).
    -   It may choose not to rebalance at all ($x_{ij}=0$) and accept high shortage ($s_i > 0$).
    -   **Result**: Minimal empty trips, but potentially poor service availability.

-   **Optimal $\lambda$ (e.g., $\lambda \approx 5$)**:
    -   Balances the two objectives.
    -   Performs rebalancing only when the cost $c_{ij}$ is "worth it" (i.e., less than the penalty of not serving).
    -   Avoids extremely long, inefficient rebalancing trips.
