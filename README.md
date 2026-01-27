# RL4AMOD with Penalty-Based Soft Constraint

> **Fork of [StanfordASL/RL4AMOD](https://github.com/StanfordASL/RL4AMOD)** with penalty-based soft constraint for rebalancing optimization.

## 🎯 Key Modification

### Problem
Original RL4AMOD forces LP to strictly achieve RL's target vehicle distribution, causing **excessive rebalancing** without considering time/opportunity costs.

### Solution
Introduced **Soft Constraint with Penalty** that allows LP to perform cost-benefit analysis:

```
Objective: minimize( rebalancing_cost + shortage_penalty × unmet_target )
```

- LP can skip expensive rebalancing if penalty cost is lower
- `shortage_penalty` parameter controls the trade-off

---

## 📁 Project Structure

```
RL4AMOD_penalty/
├── train.py                    # Training script
├── testing.py                  # Testing script
├── src/
│   ├── algos/
│   │   ├── sac.py              # SAC algorithm (main RL agent)
│   │   ├── reb_flow_solver.py  # LP solver interface (passes penalty)
│   │   └── ...
│   ├── cplex_mod/
│   │   ├── minRebDistRebOnly.mod  # ⭐ Modified LP with soft constraint
│   │   └── ...
│   ├── config/
│   │   ├── model/
│   │   │   └── sac.yaml        # SAC hyperparameters
│   │   └── simulator/
│   │       ├── macro.yaml      # Macro simulator config
│   │       └── sumo.yaml       # SUMO simulator config (+ shortage_penalty)
│   └── envs/
│       └── sim/
│           ├── macro_env.py    # Macroscopic simulator
│           └── sumo_env.py     # SUMO-based mesoscopic simulator
└── saved_files/                # Logs, checkpoints, results
```

---

## 🚀 Quick Start (Macro Environment)

### Prerequisites

```bash
pip install -r requirements.txt
```

> **Note**: CPLEX is recommended but optional. Without CPLEX, PuLP solver is used automatically.

### Training

```bash
# Basic training with SAC
python train.py simulator=macro model=sac

# Specify city and checkpoint path
python train.py simulator=macro model=sac simulator.city=nyc_brooklyn model.checkpoint_path=SAC_penalty

# Adjust training episodes
python train.py simulator=macro model=sac model.max_episodes=5000
```

### Testing

```bash
# Test trained model
python testing.py simulator=macro model=sac model.checkpoint_path=SAC_penalty

# Test with specific episodes
python testing.py simulator=macro model=sac model.test_episodes=20
```

### Key Parameters (Macro)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `simulator.city` | `nyc_brooklyn` | City dataset |
| `simulator.demand_ratio` | `0.5` | Demand scaling factor |
| `simulator.beta` | `0.5` | Rebalancing cost coefficient |
| `simulator.max_steps` | `20` | Steps per episode |
| `model.max_episodes` | `10000` | Training episodes |
| `model.batch_size` | `100` | Batch size |

---

## ⚙️ Penalty Parameter Tuning

Configure in `src/config/simulator/sumo.yaml`:

```yaml
shortage_penalty: 3.0  # Default value
```

Or override via command line:
```bash
python train.py simulator=sumo simulator.shortage_penalty=5.0
```

| Value | Behavior |
|-------|----------|
| 0.5 ~ 2.0 | Conservative rebalancing (cost priority) |
| 3.0 ~ 5.0 | Balanced trade-off |
| 10.0+ | Aggressive rebalancing (target priority) |

---

## 📊 LP Model Details

### Modified Objective Function
```
minimize(
  Σ rebFlow[e] × time[e]              // Rebalancing cost
  + shortage_penalty × Σ shortage[i]  // Penalty for unmet targets
)
```

### Soft Constraint
```
net_inflow[i] + shortage[i] >= desiredVehicles[i] - currentVehicles[i]
```

The `shortage[i]` slack variable allows regions to fall short of their target when rebalancing is too expensive.

---

## 📝 Citation

If you use this code, please cite the original work:

```bibtex
@article{gammelli2022graph,
  title={Graph neural network reinforcement learning for autonomous mobility-on-demand systems},
  author={Gammelli, Daniele and Yang, Kaidi and Harrison, James and Rodrigues, Filipe and Pereira, Francisco C and Pavone, Marco},
  journal={arXiv preprint arXiv:2104.11434},
  year={2022}
}
```

---

## 📧 Contact

- Original Authors: gammelli@stanford.edu, csasc@dtu.dk, ltresca@stanford.edu
- This Fork: effectusMOA (effectus60@naver.com)