import pandas as pd
from mesa.batchrunner import batch_run
from model import BikeModel

params = {
    "seed": range(20),  # 20 different seeds
    "connectivity": ["connected", "fragmented"],
    "n_lanes": [50, 100],
    "car_cost": 4.0,
    "beta": 0.5,
    "gamma": 1.0,
}

results = batch_run(
    BikeModel,
    parameters=params,
    max_steps=150,
    data_collection_period=-1,  # only collect at end
)

df = pd.DataFrame(results)
df.to_csv("batch_results.csv", index=False)
