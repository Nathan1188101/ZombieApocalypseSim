"""
    This code is a simple agent-based model that simulates wealth distribution.

        - Agents start with 1 wealth and move randomly to a neighboring cell. 

        - if they share a cell, one agent give money to another agent. 

        - the Gini coefficient is calculated tracks the economic inequality over time 

        - the visualization shows the agents moving around the grid and the Gini coefficient over time.

    I need to change this to simulate a zombie apocalypse.
"""

import mesa #for agent based modeling 
import seaborn as sns #data visualization 
import numpy as np #data visualization 
import pandas as pd #data visualization 
import matplotlib.pyplot as plt #data visualization 

from mesa.datacollection import DataCollector #collect data from model 
from mesa.visualization import SolaraViz, make_plot_component, make_space_component #creates a web-based visualization of the model

# function computes the Gini coefficient (economic inequality)
# it gets each agents wealth, sorts the wealth, and calculates the Gini coefficient 
"""
need to change this function to keep track of how many humans are left each step 
"""
def compute_gini(model): 
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    T = model.total_agents
    B = sum(xi * (T - i) for i, xi in enumerate(x)) / (T * sum(x))
    return 1 + (1 / T) - 2 * B

#defines each agent 
class MoneyAgent(mesa.Agent):
    """
    An agent with fixed initial wealth.
    defines an agent that has wealth and can move around a grid 

    key functions: 
    - move: moves the agent to a new position randomly to a neighboring cell 
    - give_money: transfer the money to anohther agent in the same cell 
    """

    def __init__(self, model):
        # Pass the parameters to the parent class.
        super().__init__(model)

        # Create the agent's variable and set the initial values.
        self.wealth = 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


    def give_money(self):
        """
            an agent can receive wealth from multiple other agents at once in one step
            an agent will only give wealth if they have more than 0 (obviously)
            wealth is only given if cell mates are present 
            multiple agents can receive wealth in the same step, but each giver only transfers to one recipient at a time 
            an agent giving can receive (wouldn't work in zombie apocalypse?)
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos]) #agent gets a list of all agents in the same cell 
        if len(cellmates) > 1: #if there are other agents in the same cell 
            other = self.random.choice(cellmates) #randomly select another agent 
            other.wealth += 1 #give the other agent 1 wealth
            self.wealth -= 1 #subtract 1 wealth from the agent that gave the wealth 

#defines the simulation 
class MoneyModel(mesa.Model):
    """
    A model with some number of agents.
    
    key parts: 
        - creates a grid for agents to move around on 
        - initializes the total_agents with a starting wealth of 1 
        - collects data (the Gini coefficient) at each step 
        - runs the simulation step by step 
    """
    def __init__(self, totalAgents=100, width=20, height=20):
        super().__init__()
        self.total_agents = 100
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        # Create agents
        for i in range(self.total_agents):
            agent = MoneyAgent(self)
            
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        self.running = True
        #self.datacollector.collect(self)

    def step(self):
        """Advance the model by one step."""
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

#model parameters for gui 
model_params = {
    "totalAgents": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": {
        "type": "SliderInt",
        "value": 20,
        "label": "Width:",
        "min": 10,
        "max": 100,
        "step": 10,
    },
    "height": {
        "type": "SliderInt",
        "value": 20,
        "label": "Height:",
        "min": 10,
        "max": 100,
        "step": 10,
    },
}

#modify this function to change output on grid
#settings for the agents visualization 
def agent_portrayal(agent):
#agents with more wealth appear larger and in different colors 
    size = 10
    color = "tab:red"

    if agent.wealth > 3:
        size = 80
        color = "tab:blue"
    elif agent.wealth > 2:
        size = 50
        color = "tab:green"
    elif agent.wealth > 1:
        size = 20
        color = "tab:orange"
    return {"size": size, "color": color}

#creates and runs the simulation 
money_model = MoneyModel(10, 10, 10) #initializes the model, 10x10 grid with 10 agents 

SpaceGraph = make_space_component(agent_portrayal) #creates a space to display agents 
GiniPlot=make_plot_component("Gini") #this creates a plot to keep track of the Gini coefficient 

#generates the interactive web page
page = SolaraViz(
    money_model,
    components=[SpaceGraph, GiniPlot],
    model_params=model_params,
    name="Money Model"
)
# This is required to render the visualization in the Jupyter notebook
page