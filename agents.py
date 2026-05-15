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
        
        self.time_bike =
        self.time_car = 
        self.p_bike = 

    
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
        pass
