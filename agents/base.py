"""
Base agent class that all specialized agents will inherit from.
"""

class Agent:
    def __init__(self, agent_id, name, system_prompt, temperature=0.7):
        """
        Initialize a new agent.
        
        Args:
            agent_id (str): Unique identifier for the agent
            name (str): Display name for the agent
            system_prompt (str): The system prompt that defines the agent's personality
            temperature (float): The temperature parameter for the LLM (controls randomness)
        """
        self.agent_id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.temperature = temperature
    
    def get_config(self):
        """
        Return the agent's configuration.
        
        Returns:
            dict: The agent's configuration
        """
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature
        }
    
    @classmethod
    def get_agent_id(cls):
        """
        Return the agent's ID. Should be implemented by subclasses.
        
        Returns:
            str: The agent's ID
        """
        raise NotImplementedError("Subclasses must implement get_agent_id()")