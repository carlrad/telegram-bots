"""
Agent registry module.
This module initializes and registers all available agents.
"""

from agents.assistant import AssistantAgent
from agents.chef import ChefAgent
from agents.fitness import FitnessAgent
from agents.programmer import ProgrammerAgent

# Dictionary of all available agents
AGENTS = {
    AssistantAgent.get_agent_id(): AssistantAgent(),
    ChefAgent.get_agent_id(): ChefAgent(),
    FitnessAgent.get_agent_id(): FitnessAgent(),
    ProgrammerAgent.get_agent_id(): ProgrammerAgent(),
}

def get_agent(agent_id):
    """
    Get an agent by ID.
    
    Args:
        agent_id (str): The ID of the agent to get
        
    Returns:
        Agent: The requested agent, or the default agent if not found
    """
    return AGENTS.get(agent_id, AGENTS["default"])

def get_agent_config(agent_id):
    """
    Get an agent's configuration by ID.
    
    Args:
        agent_id (str): The ID of the agent to get
        
    Returns:
        dict: The agent's configuration
    """
    return get_agent(agent_id).get_config()

def get_all_agents():
    """
    Get all available agents.
    
    Returns:
        dict: Dictionary of all available agents
    """
    return AGENTS