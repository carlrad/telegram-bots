"""
Default assistant agent implementation.
"""

from agents.base import Agent

class AssistantAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="default",
            name="Assistant",
            system_prompt="You are a helpful assistant.",
            temperature=0.7
        )
    
    @classmethod
    def get_agent_id(cls):
        return "default"