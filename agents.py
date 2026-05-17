import math

from mesa import Agent


class BikeAgent(Agent):
    ## Initiate agent instance, inherit model trait from parent class
    def __init__(self, model):
        super().__init__(model)

        ## choose work and home locations
        ## 90% of home locations are in residential, with 10% in downtown
        if self.model.random.random() < 0.9:
            self.home = self.model.random.choice(self.model.residential_cells)
        else:
            self.home = self.model.random.choice(self.model.downtown_cells)

        ## inversely, 90% of work locations are in downtown, with 10% in residential
        if self.model.random.random() > 0.9:
            self.work = self.model.random.choice(self.model.residential_cells)
        else:
            self.work = self.model.random.choice(self.model.downtown_cells)

        self.commute_path = self.get_commute_path()

        # cells with bike lanes as a fraction of total commute path (cells)
        self.lane_coverage_on_path = sum(
            self.model.grid.properties["bike_lane"].data[r][c]
            for r, c in self.commute_path
        ) / len(self.commute_path)

        self.time_bike = len(self.commute_path) * self.model.bike_speed_constant
        self.time_car = len(self.commute_path) * self.model.car_speed_constant

        ## probability of biking sampled randomly from uniform distribution
        self.p_bike = self.model.random.uniform(0, 1)
        self.mode = "bike" if self.model.random.random() < self.p_bike else "car"

    # Manhattan distance
    def get_commute_path(self):
        path = []
        r, c = self.home
        wr, wc = self.work
        while r != wr:
            r += 1 if wr > r else -1
            path.append((r, c))
        while c != wc:
            c += 1 if wc > c else -1
            path.append((r, c))
        return path

    ## Define basic decision rule
    def step(self):
        # compute route costs
        cost_bike = (
            self.time_bike - self.model.safety_bonus * self.lane_coverage_on_path
        )
        cost_car = self.time_car + self.model.car_cost

        cost_difference = cost_car - cost_bike

        # compute social fraction from Von Neumann neighbors (r=1) (based on home cell)
        neighbors = self.model.grid.get_neighbors(self.home, moore=False, radius=1)
        if neighbors:
            social_fraction = sum(1 for n in neighbors if n.mode == "bike") / len(
                neighbors
            )
        else:
            social_fraction = 0.0

        # update p_bike via logistic function
        self.p_bike = 1 / (
            1
            + math.exp(
                -(
                    self.model.beta * cost_difference
                    + self.model.gamma * social_fraction
                )
            )
        )

        # make mode choice
        self.mode = "bike" if self.model.random.random() < self.p_bike else "car"
