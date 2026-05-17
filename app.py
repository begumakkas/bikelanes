import solara
from matplotlib.figure import Figure
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.utils import update_counter
from model import BikeModel

# Define model parameters
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
        value=1.0,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
    "beta": Slider(
        label="Cost Sensitivity (β)",
        value=1.0,
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
    "bike_speed_constant": Slider(
        label="Bike Speed Constant",
        value=1.0,
        min=0.5,
        max=3.0,
        step=0.5,
    ),
    "car_speed_constant": Slider(
        label="Car Speed Constant",
        value=0.7,
        min=0.5,
        max=3.0,
        step=0.5,
    ),
    "car_cost": Slider(
        label="Car Cost Penalty",
        value=2.0,
        min=0.0,
        max=5.0,
        step=0.5,
    ),
}


def agent_portrayal(agent):
    return {
        "color": "#2ecc71" if agent.mode == "bike" else "#e74c3c",
        "marker": "s",
        "size": 20,
    }


@solara.component
def ModeSharePlot(model):
    update_counter.get()
    fig = Figure(figsize=(6, 3))
    ax = fig.subplots()

    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        ax.plot(
            data.index, data["cycling_mode_share"], color="#2ecc71", label="Bike share"
        )
        ax.axhline(
            0.5, color="gray", linestyle="--", linewidth=0.8, label="50% threshold"
        )
        ax.set_ylim(0, 1)
        ax.set_xlabel("Step")
        ax.set_ylabel("Mode Share")
        ax.set_title("Cycling Mode Share Over Time")
        ax.legend()

    solara.FigureMatplotlib(fig)


@solara.component
def LCCPlot(model):
    update_counter.get()
    fig = Figure(figsize=(6, 3))
    ax = fig.subplots()

    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        ax.plot(data.index, data["LCC"], color="#3498db", label="LCC")
        ax.set_xlabel("Step")
        ax.set_ylabel("Cells")
        ax.set_title("Largest Connected Component")
        ax.legend()

    solara.FigureMatplotlib(fig)


def get_summary(model):
    data = model.datacollector.get_model_vars_dataframe()
    if data.empty:
        return solara.Markdown("No data yet.")
    share = data["cycling_mode_share"].iloc[-1]
    lcc = data["LCC"].iloc[-1]
    return solara.Markdown(
        f"**Current bike mode share:** {share:.1%}<br>**Current LCC size:** {lcc} cells"
    )


model1 = BikeModel()

page = SolaraViz(
    model1,
    components=[
        make_plot_component({"cycling_mode_share": "#2ecc71"}),
        ModeSharePlot,
        LCCPlot,
        get_summary,
    ],
    model_params=model_params,
    name="Bike Lane ABM",
    agent_portrayal=agent_portrayal,
)

page
