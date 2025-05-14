"""
Utility functions for the Telegram bot.
"""

from agents import get_all_agents

# Store user states and conversation histories
# In a production environment, this should be stored in a database
user_data_store = {}

def get_user_data(user_id):
    """
    Get user data for a specific user.
    Initialize if this is a new user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        dict: The user's data
    """
    if user_id not in user_data_store:
        # Initialize with default values
        user_data_store[user_id] = {
            "current_agent": "default",
            "conversations": {agent_id: [] for agent_id in get_all_agents()}
        }
    
    return user_data_store[user_id]

def update_user_data(user_id, new_data):
    """
    Update user data for a specific user.
    
    Args:
        user_id: The ID of the user
        new_data (dict): The new user data
    """
    user_data_store[user_id] = new_data