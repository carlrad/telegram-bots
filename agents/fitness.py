"""
Fitness Coach Alex agent implementation.
"""

from agents.base import Agent

class FitnessAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="fitness",
            name="Fitness Coach Alex",
            system_prompt="You are Fitness Coach Alex, a certified personal trainer and nutritionist. You provide workout advice, fitness plans, and health recommendations. Be motivational and supportive.",
            temperature=0.6
        )
    
    @classmethod
    def get_agent_id(cls):
        return "fitness"