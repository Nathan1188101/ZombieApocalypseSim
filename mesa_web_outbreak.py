import mesa #for agent based modeling 
import seaborn as sns #data visualization 
import numpy as np #data visualization 
import pandas as pd #data visualization 
import matplotlib.pyplot as plt #data visualization 

from mesa.datacollection import DataCollector #collect data from model 
from mesa.visualization import SolaraViz, make_plot_component, make_space_component #creates a web-based visualization of the model

"""
Ideas for 2 small features: 

 - random chance of picking up 1 bullet each step (small chance)
 - random chance of picking up a "power up" in a random cell that will give human 100% chance of killing next zombie 
 - day night cycle? zombies move slower during day and faster at night. 
 - after certain amount of time, more humans get added as reinforcements


"""

#function to keep track of how many humans are left 
def human_count(model):
    count = 0 #initialize count of humans
    human_status = [agent.isZombie for agent in model.agents] #get the status of each agent (zombie or not)
    if False in human_status: #if there are humans in the model
        count = human_status.count(False) #count the number of humans in the model

    return count #return the count of humans
    

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
        """agent behavior each step"""
        if self.dead == True:
            return #do nothing if agent is dead 
        
        if self.isZombie == True: #if agent is a zombie
            self.move() #move the agent
            self.give_disease() #give disease to other agents in the same cell
        else: # if human 
            self.move() #move the agent
            self.shoot_zombie() #shoot a zombie if there is one in the same cell
            self.random_ammo() #random chance of picking up ammo each step

    #this function moves the agent to a new position randomly to a neighboring cell
    def move(self):
        """could also handle movement if alive in here possibly"""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps) #randomly choose a new position from the possible steps
        self.model.grid.move_agent(self, new_position) #move the agent to the new position

    #function to give disease, also 50% chance of dropping ammo to humans 
    def give_disease(self):
        """
        if agent is a zombie, and it lands on the same cell as a non zombie agent
        turn one random other non zombie agent into a zombie 
        zombies have a 50% chance of dropping some ammo to humans
        """

        cellmates = self.model.grid.get_cell_list_contents([self.pos]) #getting the agents in the same cell 

        if (len(cellmates) > 1 and self.isZombie == True): #if there are other agents in the cell and self is a zombie
            humans = [agent for agent in cellmates if agent.isZombie == False] #get the humans in the cell (filter out zombies)
            other = self.random.choice(humans) #randomly choose another agent from the human list 
            #if(other.isZombie == False): #if the randomly chosen agent is not a zombie
            other.isZombie = True #set the other agent to be a zombie

            drop = self.random.choice([True, False]) #50/50 chance of dropping ammo
            if(drop == True):
                #make sure we are only targeting humans to randomly choose to drop too instead of also considering zombies in the check
                humans = [agent for agent in cellmates if agent.isZombie == False] #get the humans in the cell
                if (humans): #if there are humans in the cell
                    ammoDrop = self.random.choice(humans) #randomly choose another agent to drop ammo (will choose same agent if only one agent in cell I think)
                    ammoDrop.shots_left += 2 #add 2 shots to the agent that drops the ammo (will play around with this number)



    #function to shoot zombie 
    def shoot_zombie(self):
        """
        if agent is human, and lands in same cell as a zombie. 
        50% chance to shoot a zombie 
        if shot success, zombie flag dead now is true (zombie dead if shot success)
        dead zombie can no longer move or infect other human agents 

        I interpreted the instructions to be that the human is always going to shoot, but the chance of killing the target is 50/50. 
        Rather than the human having a 50% chance of pulling the trigger. Overall meaning the human will always lose ammo.
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos]) #getting agents in cell 

        if(len(cellmates) > 1 and self.isZombie == False): #if other agents present and self is human 
            #filter the cellmates list to be living zombies 
            targets = [agent for agent in cellmates if agent.isZombie == True and agent.dead == False] #get the zombies in the cell that are not dead
            other = self.random.choice(targets) #randomly choose from the list of targets

            #if there are zombies in the cell and the human has shots left
            if (targets and self.shots_left > 0):
                shot = self.random.choice([True, False]) #50/50 chance of shooting zombie
                if (shot == True):
                    other.dead = True #set the zombie to dead
                    self.shots_left -= 1 #decrement shots
                else:
                    self.shots_left -= 1 #decrement shots
            
            
            """
            old implementation
            if(other.isZombie == True):
                #check how many shots left
                if(self.shots_left > 0):
                    #50% chance to shoot zombie
                    shot = self.random.choice([True, False]) #50/50 chance of shooting zombie 
                    if (shot == True):
                        other.dead = True #set the zombie to dead 
                        self.shots_left -= 1; 
                    else:
                        self.shots_left -= 1; #decrement shots 
            """
    
    #small but interesting feature to add later
    def random_ammo(self):
        """
        25% chance of picking up ammo each step
        """
        pickup = self.random.choice([True, False, False, False]) #25% chance of picking up ammo
        if(pickup == True):
            self.shots_left += 1 #add 1 to shot to ammo 


        
#define simulation 
class OutbreakModel(mesa.Model):
    """
    a model with some number of agents 
    here we are creating a model with 100 agents, 20x20 grid 
    don't think the totalAgents variable is being used here
    """
                    #took out totalAgents = 100 (after self,)
    def __init__(self, totalAgents = 100, width=20, height=20):
        super().__init__()
        self.total_agents = 100 #total number of agents
        self.grid = mesa.space.MultiGrid(width, height, True) #create a grid for agents to move around on
        self.datacollector = mesa.DataCollector(
            model_reporters={"HumanCount": human_count}, agent_reporters={"Alive": "alive"}
        )

        agentStorage = [] #a list to store agents 
        #create agents 
        for i in range(self.total_agents): #create x number of agents 
            agent = OutbreakAgent(self) #create an agent

            agentStorage.append(agent) #add the agent to the list 

            #get total amount agents and multiply by .1 
            #allAgents = self.agents #get total number of agents
            #print(len(allAgents))
            #zombieAgents = round(allAgents * .1) #10% of agents are zombies 
            #zombieAgents.isZombie = True #set the zombie flag to true for 10% of agents
            

            #add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        print(len(agentStorage)) #print the number of agents in the list
        print("-----------------")
        print(agentStorage) #print the list of agents

        #infect 10% of agents 
        #figure out the number that is 10% of the total agents, then go into that list and set the isZombie flag to true for x amount of agents
        tenPercent = round(len(agentStorage) * .1) #get 10% of the total agents
        print("10 percent of agents: ", tenPercent)
        for i in range(tenPercent): #for 10% of the agents (range takes 1 to x amount of agents)
            agentStorage[i].isZombie = True
            

        self.running = True

    def step(self):
        """Advance the model by one step"""
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

def agent_portrayal(agent):
    size = 10
    color = "tab:blue" #human

    if agent.isZombie == True:
        size = 50
        color = "tab:red" #zombie
    if agent.dead == True:
        color = "black" #dead zombie 
    return {"size": size, "color": color}   

#create and run the simulation
outbreak_model = OutbreakModel(100, 20, 20) #initializes model, 100 agents, 20x20 grid

SpaceGraph = make_space_component(agent_portrayal) #creates a space to display agents 
HumanCountPlot=make_plot_component("HumanCount") #this creates a plot to keep track of the Gini coefficient 


#generates the interactive web page
page = SolaraViz(
    outbreak_model,
    components=[SpaceGraph, HumanCountPlot],
    model_params=model_params,
    name="Outbreak Model"
)
# This is required to render the visualization in the Jupyter notebook
page
