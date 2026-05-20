import math

from mesa.discrete_space import CellAgent


class BikeAgent(CellAgent):
    ## Initiate agent, inherit model property from parent class
    def __init__(self, model, home):
        super().__init__(model)
        ## Set variable traits based on model parameters
        self.cell = home

        ## store home as cell object, use .coordinate for tuple access
        self.home = home

        ## 90% of work locations are in downtown, 10% in residential
        if self.model.random.random() < 0.9:
            self.work = self.model.random.choice(self.model.downtown_cells)
        else:
            self.work = self.model.random.choice(self.model.residential_cells)

        while self.work == self.home:
            self.work = self.model.random.choice(
                self.model.downtown_cells
                if self.model.random.random() < 0.9
                else self.model.residential_cells
            )

        # calculate commute path
        self.commute_path = self.get_commute_path()

        # calculate cells with lanes on commute path
        self.lane_coverage_on_path = sum(
            self.model.grid.bike_lane.data[r][c] for r, c in self.commute_path
        ) / len(self.commute_path)

        self.time_bike = len(self.commute_path) * self.model.bike_time_factor
        self.time_car = len(self.commute_path) * self.model.car_time_factor

        # initialize probability of biking randomly from uniform distribution
        self.p_bike = self.model.random.uniform(0, 1)
        # initialize all modes as car first
        self.mode = "car"

    # BFS search to get commute path (Manhattan distance)
    def get_commute_path(self):
        path = []
        r, c = self.home.coordinate
        wr, wc = self.work.coordinate
        while r != wr:
            r += 1 if wr > r else -1
            path.append((r, c))
        while c != wc:
            c += 1 if wc > c else -1
            path.append((r, c))
        return path

    ## Define movement action
    def step(self):
        cost_bike = (
            self.time_bike - self.model.safety_bonus * self.lane_coverage_on_path
        )
        cost_car = self.time_car + self.model.car_cost
        cost_difference = cost_car - cost_bike

        # get Von Neumann neighbors via cell connections
        neighbor_cells = self.home.connections.values()
        neighbors = [agent for cell in neighbor_cells for agent in cell.agents]
        if neighbors:
            social_fraction = sum(1 for n in neighbors if n.mode == "bike") / len(
                neighbors
            )
        else:
            social_fraction = 0.0

        self.p_bike = 1 / (
            1
            + math.exp(
                -(
                    self.model.beta * cost_difference
                    + self.model.gamma * social_fraction
                )
            )
        )
        ## deterministic choice to bike
        self.mode = "bike" if self.p_bike > self.model.bike_threshold else "car"
