from mesa import Agent


class BikeAgent(Agent):
    ## Initiate agent instance, inherit model trait from parent class
    def __init__(self, model):
        super().__init__(model)

    ## Define basic decision rule
    def step(self):
        pass
