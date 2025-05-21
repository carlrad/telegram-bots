"""
Telegram bot handlers for processing commands and messages.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio

from agents import get_agent_config, get_all_agents
from services import openai_service
from bot.utils import get_user_data, update_user_data
import config

logger = logging.getLogger(__name__)

async def check_authorization(update: Update) -> bool:
    """Check if the user is authorized to use the bot."""
    user_id = update.effective_user.id
    if user_id not in config.ALLOWED_USERS:
        logger.warning(f"Unauthorized access attempt from user ID: {user_id}")
        await update.message.reply_text(
            "Sorry, you're not authorized to use this bot. Please contact the bot owner for access."
        )
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    if not await check_authorization(update):
        return
        
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data if this is a new user
    user_data = get_user_data(user_id)
    
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your AI assistant hub. You can talk to different AI agents with different specialties.\n\n"
        f"Currently speaking with: {get_agent_config(user_data['current_agent'])['name']}\n\n"
        "Use /agents to change who you're talking to, or /help for more commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    if not await check_authorization(update):
        return
        
    help_text = """
Available commands:
/start - Start the conversation
/help - Show this help message
/agents - Choose which agent to talk to
/reset - Reset conversation with current agent
/mealplan - Generate a weekly meal plan (you can add preferences too)
    
Special features:
- When talking to Chef Gordon, ask for a "meal plan" to get a weekly meal plan
- You can specify preferences like: "I prefer Italian food and like chicken"
- You can specify restrictions like: "I'm allergic to nuts and avoid dairy"
    
Examples:
/mealplan pref:italian pref:quick servings:5
/mealplan avoid:nuts avoid:dairy
    
Just type any message to chat with the current agent!
    """
    await update.message.reply_text(help_text)

async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display buttons to select different agents."""
    if not await check_authorization(update):
        return
        
    keyboard = []
    
    # Create a button for each agent
    for agent_id, agent in get_all_agents().items():
        keyboard.append([InlineKeyboardButton(agent.name, callback_data=f"agent_{agent_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an agent to talk to:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Check authorization for button callbacks
    if user_id not in config.ALLOWED_USERS:
        logger.warning(f"Unauthorized button press attempt from user ID: {user_id}")
        await query.answer("You are not authorized to use this bot.", show_alert=True)
        return
        
    await query.answer()
    
    # Extract the agent ID from the callback data
    if query.data.startswith("agent_"):
        agent_id = query.data[6:]  # Remove 'agent_' prefix
        
        # Get user data
        user_data = get_user_data(user_id)
        
        # Update the current agent
        user_data["current_agent"] = agent_id
        update_user_data(user_id, user_data)
        
        # Get the agent's name
        agent_name = get_agent_config(agent_id)["name"]
        
        await query.edit_message_text(
            f"You are now talking to {agent_name}. How can I help you?"
        )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation with the current agent."""
    if not await check_authorization(update):
        return
        
    user_id = update.effective_user.id
    
    # Get user data
    user_data = get_user_data(user_id)
    current_agent = user_data["current_agent"]
    
    # Reset the conversation history for the current agent
    user_data["conversations"][current_agent] = []
    update_user_data(user_id, user_data)
    
    # Get the agent's name
    agent_name = get_agent_config(current_agent)["name"]
    
    await update.message.reply_text(
        f"Your conversation with {agent_name} has been reset."
    )

async def meal_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send a personalized meal plan."""
    if not await check_authorization(update):
        return
        
    user_id = update.effective_user.id
    
    # Get user data using your utility function
    user_data = get_user_data(user_id)
    
    # Force agent to be chef
    user_data["current_agent"] = "chef"
    update_user_data(user_id, user_data)
    
    await update.message.reply_text(
        "Chef Gordon is preparing a personalized meal plan. This will take a moment..."
    )
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Import the chef agent class directly
        from agents.chef import ChefAgent
        chef_agent = ChefAgent()
        
        # Get preferences from command arguments if provided
        preferences = []
        restrictions = []
        servings = 4
        
        if context.args:
            for arg in context.args:
                if arg.startswith("pref:"):
                    preferences.append(arg[5:])
                elif arg.startswith("avoid:"):
                    restrictions.append(arg[6:])
                elif arg.startswith("servings:"):
                    try:
                        servings = int(arg[9:])
                    except ValueError:
                        pass
        
        # Create a specialized prompt for meal planning
        meal_plan_prompt = chef_agent.format_meal_plan_prompt(
            preferences=preferences if preferences else None,
            restrictions=restrictions if restrictions else None,
            servings=servings
        )
        
        # Create system message with the chef's system prompt
        messages = [
            {"role": "system", "content": chef_agent.system_prompt},
            {"role": "user", "content": meal_plan_prompt}
        ]
        
        # Call OpenAI API through your service
        raw_meal_plan = openai_service.generate_response(
            messages=messages,
            max_tokens=2000,  # Increased token limit
            temperature=chef_agent.temperature
        )
        
        # Add to conversation history
        if "chef" not in user_data["conversations"]:
            user_data["conversations"]["chef"] = []
        
        user_data["conversations"]["chef"].append({"role": "user", "content": meal_plan_prompt})
        user_data["conversations"]["chef"].append({"role": "assistant", "content": raw_meal_plan})
        update_user_data(user_id, user_data)
        
        # Parse the response
        structured_plan = chef_agent.parse_meal_plan_response(raw_meal_plan)
        
        # Format the structured plan into multiple messages
        message_parts = chef_agent.format_structured_meal_plan(structured_plan)
        
        # Log information about the message parts
        logger.info(f"Meal plan split into {len(message_parts)} parts")
        for i, part in enumerate(message_parts):
            logger.info(f"Part {i+1} length: {len(part)} characters")
        
        # Send each part as a separate message
        for part in message_parts:
            if part.strip():  # Only send non-empty parts
                await update.message.reply_text(part)
                # Brief delay to maintain message order
                await asyncio.sleep(0.5)
                
    except Exception as e:
        logger.error(f"Error generating meal plan: {e}")
        await update.message.reply_text(
            "I'm sorry, I encountered an error while creating your meal plan. Please try again later."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and respond using the selected agent's personality."""
    if not await check_authorization(update):
        return
        
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Get user data
    user_data = get_user_data(user_id)
    current_agent_id = user_data["current_agent"]
    
    # Get the current agent config
    current_agent = get_agent_config(current_agent_id)
    
    # Add user message to the conversation history
    if current_agent_id not in user_data["conversations"]:
        user_data["conversations"][current_agent_id] = []
    
    user_data["conversations"][current_agent_id].append({"role": "user", "content": user_message})
    
    # Special handling for meal plan requests when talking to the chef
    if current_agent_id == "chef" and any(keyword in user_message.lower() for keyword in ["meal plan", "weekly plan", "plan meals"]):
        # Extract possible preferences/restrictions from the message
        preferences = []
        restrictions = []
        servings = 4
        
        # Very basic parsing - in a real app, this would be more sophisticated
        if "prefer" in user_message.lower() or "like" in user_message.lower():
            # Try to extract preferences after keywords
            for keyword in ["prefer", "like", "enjoy", "want"]:
                if keyword in user_message.lower():
                    parts = user_message.lower().split(keyword)
                    if len(parts) > 1:
                        possible_prefs = parts[1].split(",")
                        for pref in possible_prefs:
                            # Clean up the preference
                            clean_pref = pref.strip().strip(".:!?")
                            if clean_pref and len(clean_pref) > 2:  # Avoid single letters
                                preferences.append(clean_pref)
        
        if "avoid" in user_message.lower() or "allerg" in user_message.lower() or "don't like" in user_message.lower():
            # Try to extract restrictions
            for keyword in ["avoid", "allerg", "don't like", "cannot eat", "can't eat"]:
                if keyword in user_message.lower():
                    parts = user_message.lower().split(keyword)
                    if len(parts) > 1:
                        possible_restrictions = parts[1].split(",")
                        for restriction in possible_restrictions:
                            # Clean up the restriction
                            clean_restriction = restriction.strip().strip(".:!?")
                            if clean_restriction and len(clean_restriction) > 2:  # Avoid single letters
                                restrictions.append(clean_restriction)
        
        # Create a specialized prompt for meal planning
        from agents.chef import ChefAgent
        chef_agent = ChefAgent()
        meal_plan_prompt = chef_agent.format_meal_plan_prompt(
            preferences=preferences if preferences else None,
            restrictions=restrictions if restrictions else None,
            servings=servings
        )
        
        # Create system message with the chef's system prompt
        messages = [
            {"role": "system", "content": chef_agent.system_prompt},
            {"role": "user", "content": meal_plan_prompt}
        ]
        
        # Call OpenAI API through your service
        raw_meal_plan = openai_service.generate_response(
            messages=messages,
            max_tokens=2000,  # Increased token limit
            temperature=chef_agent.temperature
        )
        
        # Add to conversation history
        user_data["conversations"][current_agent_id].append({"role": "user", "content": meal_plan_prompt})
        user_data["conversations"][current_agent_id].append({"role": "assistant", "content": raw_meal_plan})
        update_user_data(user_id, user_data)
        
        # Parse the response
        structured_plan = chef_agent.parse_meal_plan_response(raw_meal_plan)
        
        # Format the structured plan into multiple messages
        message_parts = chef_agent.format_structured_meal_plan(structured_plan)
        
        # Send each part as a separate message
        for part in message_parts:
            if part.strip():  # Only send non-empty parts
                await update.message.reply_text(part)
                # Brief delay to maintain message order
                await asyncio.sleep(0.5)
        
        return
    
    # Get the conversation history for the current agent
    conversation_history = user_data["conversations"][current_agent_id]
    
    # Create the messages list for the API call
    messages = [
        {"role": "system", "content": current_agent["system_prompt"]},
        *conversation_history[-config.MAX_HISTORY_LENGTH:]  # Only use the last N messages
    ]
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Call OpenAI API through your service
        response = openai_service.generate_response(
            messages=messages,
            max_tokens=config.DEFAULT_MAX_TOKENS,
            temperature=current_agent["temperature"]
        )
        
        # Add the response to the conversation history
        user_data["conversations"][current_agent_id].append({"role": "assistant", "content": response})
        update_user_data(user_id, user_data)
        
        # Send the response
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text(
            "I'm sorry, I encountered an error while processing your message. Please try again later."
        )