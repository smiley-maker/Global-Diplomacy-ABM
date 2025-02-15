# abm_model.py (excerpt)
import random
import networkx as nx
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import models.config as config  # Import the configuration settings

class CountryAgent(Agent):
    def __init__(self, unique_id, model, diplomatic_priority, region):
        super().__init__(unique_id, model)
        self.diplomatic_priority = diplomatic_priority
        self.region = region
        self.current_ties = set()

    def step(self):
        # Agent decision-making using probabilities from the model
        potential_partners = [agent for agent in self.model.schedule.agents if agent.unique_id != self.unique_id]
        for partner in potential_partners:
            if partner.unique_id not in self.current_ties:
                p_form = self.model.tie_formation_prob(self, partner)
                if random.random() < p_form:
                    self.current_ties.add(partner.unique_id)
                    partner.current_ties.add(self.unique_id)
                    self.model.G.add_edge(self.unique_id, partner.unique_id)
            else:
                p_maintain = self.model.tie_maintenance_prob(self, partner)
                if random.random() > p_maintain:
                    self.current_ties.remove(partner.unique_id)
                    partner.current_ties.remove(self.unique_id)
                    if self.model.G.has_edge(self.unique_id, partner.unique_id):
                        self.model.G.remove_edge(self.unique_id, partner.unique_id)

class DiplomaticModel(Model):
    def __init__(self):
        self.num_agents = config.NUM_AGENTS
        self.schedule = RandomActivation(self)
        self.G = nx.Graph()
        self.datacollector = DataCollector(
            model_reporters={"Number_of_Ties": self.compute_total_ties},
            agent_reporters={"Diplomatic_Priority": "diplomatic_priority", "Region": "region"}
        )

        for i in range(self.num_agents):
            diplomatic_priority = random.uniform(config.MIN_DIPLOMATIC_PRIORITY, config.MAX_DIPLOMATIC_PRIORITY)
            region = random.choice(config.REGIONS)
            agent = CountryAgent(i, self, diplomatic_priority, region)
            self.schedule.add(agent)
            self.G.add_node(i)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def tie_formation_prob(self, agent_a, agent_b):
        # Use configuration values for probability calculations
        region_factor = config.REGION_FACTOR_SAME if agent_a.region == agent_b.region else config.REGION_FACTOR_DIFFERENT
        avg_priority = (agent_a.diplomatic_priority + agent_b.diplomatic_priority) / 2
        prob = config.BASE_TIE_FORMATION_PROB * avg_priority * region_factor
        return min(prob, 1.0)

    def tie_maintenance_prob(self, agent_a, agent_b):
        return config.TIE_MAINTENANCE_PROB

    def compute_total_ties(self):
        return self.G.number_of_edges()

if __name__ == "__main__":
    model = DiplomaticModel()
    for _ in range(config.NUM_STEPS):
        model.step()
    print("Total diplomatic ties:", model.compute_total_ties())
    nx.write_gexf(model.G, "diplomatic_network.gexf")
