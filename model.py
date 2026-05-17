from agents import BikeAgent
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space.property_layer import PropertyLayer
from mesa.space import SingleGrid


class BikeModel(Model):
    def __init__(
        self,
        width=20,
        height=20,
        n_lanes=50,
        connectivity="fragmented",
        bike_speed_constant=1.0,
        car_speed_constant=0.7,
        safety_bonus=1.0,
        car_cost=2.0,
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
        self.bike_speed_constant = bike_speed_constant
        self.car_speed_constant = car_speed_constant
        self.safety_bonus = safety_bonus
        self.car_cost = car_cost
        self.beta = beta
        self.gamma = gamma

        self.grid = SingleGrid(width, height, torus=False)

        self.downtown_cells = [
            (r, c)
            for r in range(height)
            for c in range(width)
            if self.get_zone(r, c) == "downtown"
        ]
        self.residential_cells = [
            (r, c)
            for r in range(height)
            for c in range(width)
            if self.get_zone(r, c) == "residential"
        ]

        # Initialize bike lane property layer
        bike_lane_layer = PropertyLayer("bike_lane", width, height, False)
        self.grid.add_property_layer(bike_lane_layer)

        if self.connectivity == "connected":
            self.place_connected_lanes(self.n_lanes)
        else:
            self.place_fragmented_lanes(self.n_lanes)

        # Assign unique home cells: 90% residential, 10% downtown
        n_residential = int(0.9 * (width * height))
        n_downtown = (width * height) - n_residential

        home_cells = self.random.sample(
            self.residential_cells, min(n_residential, len(self.residential_cells))
        ) + self.random.sample(
            self.downtown_cells, min(n_downtown, len(self.downtown_cells))
        )

        # Place agents at their home cells
        for home in home_cells:
            agent = BikeAgent(self, home)
            self.grid.place_agent(agent, home)

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
            if self.grid.properties["bike_lane"].data[r][c]
        )
        visited = set()
        largest = 0

        for cell in lane_cells:
            if cell not in visited:
                # BFS from this cell
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

    ## Divide grid into three zones: downtown (work), middle (mix of work and home), and residential (home)
    @staticmethod
    def get_zone(row, col, grid_size=20):
        center = grid_size / 2
        distance = max(abs(row - center), abs(col - center))  # distance from center
        if distance < 5:
            return "downtown"
        else:
            return "residential"

    # BFS
    def place_connected_lanes(self, n_lanes):
        # start from a random cell near center
        start = (self.height // 2, self.width // 2)
        self.grid.properties["bike_lane"].data[start[0]][start[1]] = True
        placed = {start}
        frontier = self.get_lane_neighbors(*start)

        while len(placed) < n_lanes and frontier:
            # pick a random cell from the frontier and place a lane
            next_cell = self.random.choice(frontier)
            frontier.remove(next_cell)
            if next_cell not in placed:
                self.grid.properties["bike_lane"].data[next_cell[0]][next_cell[1]] = (
                    True
                )
                placed.add(next_cell)
                for neighbor in self.get_lane_neighbors(*next_cell):
                    if neighbor not in placed and neighbor not in frontier:
                        frontier.append(neighbor)

    def place_fragmented_lanes(self, n):
        all_cells = [(r, c) for r in range(self.height) for c in range(self.width)]
        cells = self.random.sample(all_cells, n)
        for r, c in cells:
            self.grid.properties["bike_lane"].data[r][c] = True

    ## Define step:
    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
