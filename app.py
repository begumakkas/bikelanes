import solara
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle
from model import BikeModel

## Define variable model parameters
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "n_lanes": Slider(
        label="Number of Bike Lane Cells",
        value=50,
        min=0,
        max=200,
        step=10,
    ),
    "connectivity": {
        "type": "Select",
        "value": "fragmented",
        "values": ["fragmented", "connected"],
        "label": "Lane Connectivity",
    },
    "safety_bonus": Slider(
        label="Safety Bonus",
        value=2.0,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
    "beta": Slider(
        label="Cost Sensitivity (β)",
        value=0.5,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
    "gamma": Slider(
        label="Social Influence (γ)",
        value=1.0,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
    "bike_time_factor": Slider(
        label="Bike Time Constant",
        value=1.0,
        min=0.5,
        max=3.0,
        step=0.5,
    ),
    "car_time_factor": Slider(
        label="Car Time Constant",
        value=0.7,
        min=0.5,
        max=3.0,
        step=0.5,
    ),
    "car_cost": Slider(
        label="Car Cost Penalty",
        value=4.0,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
}


## Define agent portrayal (color, marker, size)
def agent_portrayal(agent):
    return AgentPortrayalStyle(
        color="#2ecc71" if agent.mode == "bike" else "#e74c3c",
        marker="s",
        size=20,
    )


## Define bike lane portayal
def propertylayer_portrayal(layer):
    return PropertyLayerStyle(
        color="#02C39A", alpha=0.3, colorbar=False, vmin=0, vmax=1
    )


## Summarize current bike mode share and LCC size
def get_summary(model):
    data = model.datacollector.get_model_vars_dataframe()
    if data.empty:
        return solara.Markdown("No data yet.")
    share = data["cycling_mode_share"].iloc[-1]
    lcc = data["LCC"].iloc[-1]
    return solara.Markdown(
        f"**Current bike mode share:** {share:.1%}<br>**Current LCC size:** {lcc} cells"
    )


## Instantiate model
model = BikeModel()

## Define model plot component based on above
ModeSharePlot = make_plot_component("cycling_mode_share")

## Define model space component based on above
SpaceGraph = make_space_component(
    agent_portrayal, propertylayer_portrayal=propertylayer_portrayal
)

## Define all aspects of page
page = SolaraViz(
    model,
    components=[
        SpaceGraph,
        ModeSharePlot,
        get_summary,
    ],
    model_params=model_params,
    name="Bike Lane ABM",
    agent_portrayal=agent_portrayal,
)

## Return page
page
