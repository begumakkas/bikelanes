# Does Network Connectivity Matter More Than Coverage? Simulating Bike Lane Effects on Cycling Adoption

**Begum Akkas** 

## Overview

This project uses an agent-based model (ABM) to investigate whether the spatial connectivity of a bike lane network has a greater effect on cycling mode share than total lane coverage. Rather than calibrating to a specific city, the model is a stylized urban environment designed to isolate connectivity as an independent variable, which that cannot be cleanly done with observational data, where more connected networks also tend to have more total infrastructure.

The core comparison: a smaller but spatially coherent (connected) bike lane network vs. a larger but fragmented one. If the connected network produces higher equilibrium cycling mode share, this supports the primacy of connectivity over coverage in driving mode shift.

## Research Question

> Does the connectivity of a bike lane network have a greater effect on cycling mode share than total lane coverage?

## Model Description

### Environment

- 20×20 grid representing a generic urban environment
- Cells assigned as **downtown** (within distance 4 of center) or **residential**
- Bike lane presence stored as a Boolean property layer, fixed at initialization

### Agents

300 agents represent urban commuters making a daily binary mode choice: **bike or drive**. Each agent has:

- A fixed home cell (90% residential, 10% downtown)
- A fixed work cell (90% downtown, 10% residential)
- A precomputed Manhattan-distance commute path
- A `lane_coverage_on_path` value (fraction of commute path covered by bike lanes)
- Travel time constants for biking and driving
- A `p_bike` probability that updates each step

### Step Logic

Each step, agents:

1. Compute a cost difference between biking and driving:
   ```
   cost_bike = time_bike − safety_bonus × lane_coverage_on_path
   cost_car  = time_car + car_cost
   cost_diff = cost_car − cost_bike
   ```
2. Observe the share of neighboring agents currently biking (`social_fraction`)
3. Update `p_bike` via a binary logistic function:
   ```
   p_bike = 1 / (1 + exp(−(β × cost_diff + γ × social_fraction)))
   ```
4. Choose to bike deterministically if `p_bike > 0.5`

### Bike Lane Placement

Two placement strategies, both placing the same total number of lane cells `N`:

- **Connected**: BFS expansion from a central seed cell, producing a single contiguous component
- **Fragmented**: Uniform random sampling of `N` cells with no adjacency constraint

Connectivity is measured as the size of the **largest connected component (LCC)** of lane cells using Von Neumann neighborhoods.

### Scenarios

| Scenario | Lane Count | Connectivity |
|---|---|---|
| Baseline | 0 | — |
| Low coverage, fragmented | 50 | Low |
| Low coverage, connected | 50 | High |
| High coverage, fragmented | 100 | Low |
| High coverage, connected | 100 | High |

Each scenario is run 20 times with different random seeds. Equilibrium mode share is recorded at step 100 (convergence typically occurs within 5–10 steps).

### Key Parameters

| Parameter | Value | Description |
|---|---|---|
| `β` | 0.5 | Sensitivity to cost difference |
| `γ` | 1.0 | Weight on social observation |
| `safety_bonus` | 2.0 | Perceived safety benefit of biking on lanes |
| `car_cost` | 4.0 | Flat penalty representing parking and fuel |

## Key Findings

- A connected network of **50 lanes** achieves a mean cycling mode share of **15.8%**, outperforming a fragmented network of **100 lanes** (12.9%), a statistically significant difference (p < 0.001)
- The connectivity advantage persists at equal coverage levels: connected placement consistently outperforms fragmented placement regardless of total lane count
- The connectivity gain is approximately **4 percentage points** at both coverage levels, suggesting connectivity and coverage operate as largely independent drivers of mode share
- The `safety_bonus` parameter is consequential: the connectivity effect only emerges when infrastructure provides meaningful safety improvements

## Running the Model

### Requirements

```bash
uv add mesa
```

### Interactive GUI

```bash
solara run app.py
```

### Batch Runs / Analysis

```bash
uv run batch_run.py
```


## Repository Structure

```
.
├── README.md
├── Report.docx
├── agents.py                       # agent specifications
├── app.py                          # Solara visualization app
├── batch_results.csv               # batch run results
├── batch_results.png               # viz results
├── batch_run.py                    # batch run file
├── bike_abm_presentation.pptx
├── model.py                        # model specifications
└── viz.ipynb                       # visualize batch run
```

## References

- Aziz, H. M. A., Park, B. H., Morton, A., Stewart, R. N., Hilliard, M., & Maness, M. (2018). A high resolution agent-based model to support walk-bicycle infrastructure investment decisions: A case study with New York City. *Transportation Research Part C*, 86, 280–299.
- Hwang, U., Kim, I., Guhathakurta, S., & Van Hentenryck, P. (2024). Comparing different methods for connecting bike lanes to generate a complete bike network and identify potential complete streets in Atlanta. *Journal of Cycling and Micromobility Research*, 2, 100028.
- Jafari, A., et al. (2025). Understanding the impact of city-wide cycling corridors on cycling mode share among different demographic clusters in Greater Melbourne, Australia. *Transportation*.
- Kaziyeva, D., Loidl, M., & Wallentin, G. (2021). Simulating spatio-temporal patterns of bicycle flows with an agent-based model. *ISPRS International Journal of Geo-Information*, 10(2), 88.
- Marshall, W. E., & Ferenchak, N. N. (2019). Why cities with high bicycling rates are safer for all road users. *Journal of Transport & Health*, 13, 100539.
- Schön, P., Heinen, E., & Manum, B. (2024). A scoping review on cycling network connectivity and its effects on cycling. *Transport Reviews*, 44(4), 912–936.
