import mesa #for agent based modeling 
import seaborn as sns #data visualization 
import numpy as np #data visualization 
import pandas as pd #data visualization 
import matplotlib.pyplot as plt #data visualization 

from mesa.datacollection import DataCollector #collect data from model 
from mesa.visualization import SolaraViz, make_plot_component, make_space_component #creates a web-based visualization of the model


#function to keep track of how many humans are left 


#define agent 
class OutbreakAgent(mesa.Agent):
    """
    Moves randomly around the grid
    Has a flag isZombie
    has a variable shots_left = 15 
    has flag dead 

    when creating agents make 10% of them zombies 
    """

    def __init__(self, model):
        # Pass the parameters to the parent class
        super().__init__(model)
        #creating the agent's variable and setting initial values. 
        self.isZombie = False #set this to true for a random 10% of agents later? 
        self.shots_left = 15 
        self.dead = False 

    def step(self): 
        self.move()
        #figure this part out 
        #if self is zombie, give zombie? 

    #this function moves the agent to a new position randomly to a neighboring cell
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps) #randomly choose a new position from the possible steps
        self.model.grid.move_agent(self, new_position) #move the agent to the new position

    #function to give disease 
    def give_disease(self):
        """
        if agent is a zombie, and it lands on the same cell as a non zombie agent
        turn one random other non zombie agent into a zombie 
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos]) #getting the agents in the same cell 
        if (len(cellmates) > 1 and self.isZombie == True): #if there are other agents in the cell and self is a zombie
            other = self.random.choice(cellmates) #randomly choose another agent
            if(other.isZombie == False): #if the randomly chosen agent is not a zombie
                other.isZombie = True #set the other agent to be a zombie

    #function to shoot zombie 
    def shoot_zombie(self):
        """
        if agent is human, and lands in same cell as a zombie. 
        50% chance to shoot a zombie 
        if shot success, zombie flag dead now is true (zombie dead if shot success)
        dead zombie can no longer move or infect other human agents 
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos]) #getting agents in cell 
        if(len(cellmates) > 1 and self.isZombie == False): #if other agents present and self is human 
            other = self.random.choice(cellmates) #randomly choose another agent 
            if(other.isZombie == True):
                #check how many shots left
                if(self.shots_left > 0):
                    #50% chance to shoot zombie
                    shot = self.random.choice([True, False]) #50/50 chance of shooting zombie 
                    if (shot == True):
                        other.dead = True #set the zombie to dead 
                        self.shots_left -= 1; 
                    else:
                        self.shots_left -= 1; 

        


