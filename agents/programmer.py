"""
Dev Maya programmer agent implementation.
"""

from agents.base import Agent

class ProgrammerAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="programmer",
            name="Dev Maya",
            system_prompt="You are Dev Maya, an expert software developer with expertise in multiple programming languages. You help with coding problems, explain technical concepts, and provide code examples. Be precise and technical.",
            temperature=0.5
        )
    
    @classmethod
    def get_agent_id(cls):
        return "programmer"