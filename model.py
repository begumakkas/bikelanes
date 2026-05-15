import random

from agents import SamaritanAgent
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space.property_layer import PropertyLayer
from mesa.space import SingleGrid


class BikeModel(Model):
    def __init__(self, width=20, height=20, radius=1, connectivity=False, seed=None):
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)
        self.width = width
        self.height = height
        self.radius = radius
        self.grid = SingleGrid(width, height, torus=False)
        self.connectivity = connectivity

        self.downtown_cells = [
            (r, c)
            for r in range(20)
            for c in range(20)
            if self.get_zone(r, c) == "downtown"
        ]
        self.residential_cells = [
            (r, c)
            for r in range(20)
            for c in range(20)
            if self.get_zone(r, c) == "residential"
        ]

        ## Add two property layers: 1) bike lane (boolean), 2) zone type (downtown vs residential)
        # 1. Initialize empty bike lane layer
        bike_lane_layer = PropertyLayer("bike_lane", 20, 20, False)
        self.grid.add_property_layer(bike_lane_layer)

        # 2. Populate it with placement function matches scenario
        if self.connectivity == "connected":
            self.place_connected_lanes(self.n_lanes)
        else:
            self.place_fragmented_lanes(self.n_lanes)

        ## Define data collector
        self.datacollector = DataCollector(
            model_reporters={
                ## populate
            }
        )

        ## Place agents on the grid
        for x in range(self.width):
            for y in range(self.height):
                agent = SamaritanAgent(self)
                self.grid.place_agent(agent, (x, y))

        ## Initialize datacollector
        self.datacollector.collect(self)

    ## Define step:
    def step(self):
        pass

    ## Divide grid into three zones: downtown (work), middle (mix of work and home), and residential (home)
    def get_zone(row, col, grid_size=20):
        center = grid_size / 2
        distance = max(abs(row - center), abs(col - center))  # distance from center
        if distance < 5:
            return "downtown"
        else:
            return "residential"

    def place_connected_lanes(self):
        pass

    def place_fragmented_lanes(self, n):
        # to do: initialize all_cells
        cells = random.sample(list(self.all_cells), n)
        for r, c in cells:
            self.grid.properties["bike_lane"].data[r][c] = True
