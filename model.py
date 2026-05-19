import numpy as np
from agents import BikeAgent
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.discrete_space.property_layer import PropertyLayer


class BikeModel(Model):
    def __init__(
        self,
        width=20,
        height=20,
        n_lanes=50,
        connectivity="fragmented",
        bike_time_factor=1.5,
        car_time_factor=0.7,
        safety_bonus=1.0,
        car_cost=2.0,
        bike_threshold=0.5,
        beta=1.0,
        gamma=1.0,
        seed=None,
    ):
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)

        self.width = width
        self.height = height
        self.n_lanes = n_lanes
        self.connectivity = connectivity
        self.bike_time_factor = bike_time_factor
        self.car_time_factor = car_time_factor
        self.safety_bonus = safety_bonus
        self.car_cost = car_cost
        self.beta = beta
        self.gamma = gamma
        self.bike_threshold = bike_threshold

        self.grid = OrthogonalVonNeumannGrid(
            (width, height), torus=False, random=self.random
        )

        self.downtown_cells = [
            self.grid[(r, c)]
            for r in range(height)
            for c in range(width)
            if self.get_zone(r, c) == "downtown"
        ]
        self.residential_cells = [
            self.grid[(r, c)]
            for r in range(height)
            for c in range(width)
            if self.get_zone(r, c) == "residential"
        ]

        # Initialize bike lane property layer
        bike_lane_data = np.zeros((width, height), dtype=float)
        bike_lane_layer = PropertyLayer.from_data("bike_lane", bike_lane_data)
        self.grid.add_property_layer(bike_lane_layer)

        if self.connectivity == "connected":
            self.place_connected_lanes(self.n_lanes)
        else:
            self.place_fragmented_lanes(self.n_lanes)

        # Assign unique home cells: 90% residential, 10% downtown
        n_agents = 300
        n_residential = int(0.9 * n_agents)
        n_downtown = n_agents - n_residential

        home_cells = self.random.sample(
            self.residential_cells, min(n_residential, len(self.residential_cells))
        ) + self.random.sample(
            self.downtown_cells, min(n_downtown, len(self.downtown_cells))
        )

        # Place agents at their home cells
        for home_cell in home_cells:
            BikeAgent(self, home_cell)

        self.datacollector = DataCollector(
            model_reporters={
                "cycling_mode_share": lambda m: (
                    sum(1 for a in m.agents if a.mode == "bike") / len(m.agents)
                ),
                "LCC": lambda m: m.compute_lcc(),
            }
        )

        self.datacollector.collect(self)

    def get_lane_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors.append((nr, nc))
        return neighbors

    def compute_lcc(self):
        lane_cells = set(
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if self.grid.bike_lane.data[r][c]
        )
        visited = set()
        largest = 0

        for cell in lane_cells:
            if cell not in visited:
                component_size = 0
                queue = [cell]
                visited.add(cell)
                while queue:
                    current = queue.pop(0)
                    component_size += 1
                    for neighbor in self.get_lane_neighbors(*current):
                        if neighbor in lane_cells and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                largest = max(largest, component_size)

        return largest

    @staticmethod
    def get_zone(row, col, grid_size=20):
        center = grid_size / 2
        distance = max(abs(row - center), abs(col - center))
        if distance < 5:
            return "downtown"
        else:
            return "residential"

    def place_connected_lanes(self, n_lanes):
        start = (self.height // 2, self.width // 2)
        self.grid.bike_lane.data[start[0]][start[1]] = 1.0
        placed = {start}
        frontier = self.get_lane_neighbors(*start)

        while len(placed) < n_lanes and frontier:
            next_cell = self.random.choice(frontier)
            frontier.remove(next_cell)
            if next_cell not in placed:
                self.grid.bike_lane.data[next_cell[0]][next_cell[1]] = 1.0
                placed.add(next_cell)
                for neighbor in self.get_lane_neighbors(*next_cell):
                    if neighbor not in placed and neighbor not in frontier:
                        frontier.append(neighbor)

    def place_fragmented_lanes(self, n):
        all_cells = [(r, c) for r in range(self.height) for c in range(self.width)]
        cells = self.random.sample(all_cells, n)
        for r, c in cells:
            self.grid.bike_lane.data[r][c] = 1.0

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

        ## stopping condition
        if self.steps >= 100:
            self.running = False
