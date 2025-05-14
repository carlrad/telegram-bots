import os
import logging
import json
from dotenv import load_dotenv
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set your API tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Define different agent personalities
AGENTS = {
    "default": {
        "name": "Assistant",
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7
    },
    "chef": {
        "name": "Chef Gordon",
        "system_prompt": "You are Chef Gordon, a professional chef with 20 years of experience. You specialize in providing cooking advice, recipes, and culinary tips. Be enthusiastic about food and cooking.",
        "temperature": 0.8
    },
    "fitness": {
        "name": "Fitness Coach Alex",
        "system_prompt": "You are Fitness Coach Alex, a certified personal trainer and nutritionist. You provide workout advice, fitness plans, and health recommendations. Be motivational and supportive.",
        "temperature": 0.6
    },
    "programmer": {
        "name": "Dev Maya",
        "system_prompt": "You are Dev Maya, an expert software developer with expertise in multiple programming languages. You help with coding problems, explain technical concepts, and provide code examples. Be precise and technical.",
        "temperature": 0.5
    }
}

# Store user states and conversation histories
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data if this is a new user
    if user_id not in user_data:
        user_data[user_id] = {
            "current_agent": "default",
            "conversations": {agent_id: [] for agent_id in AGENTS}
        }
    
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your AI assistant hub. You can talk to different AI agents with different specialties.\n\n"
        f"Currently speaking with: {AGENTS[user_data[user_id]['current_agent']]['name']}\n\n"
        "Use /agents to change who you're talking to, or /help for more commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    help_text = """
Available commands:
/start - Start the conversation
/help - Show this help message
/agents - Choose which agent to talk to
/reset - Reset conversation with current agent
    
Just type any message to chat with the current agent!
    """
    await update.message.reply_text(help_text)

async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display buttons to select different agents."""
    keyboard = []
    for agent_id, agent_info in AGENTS.items():
        keyboard.append([InlineKeyboardButton(agent_info["name"], callback_data=f"agent_{agent_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an agent to talk to:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    # Extract the agent ID from the callback data
    if query.data.startswith("agent_"):
        agent_id = query.data[6:]  # Remove 'agent_' prefix
        if agent_id in AGENTS:
            user_id = query.from_user.id
            
            # Initialize user data if needed
            if user_id not in user_data:
                user_data[user_id] = {
                    "current_agent": "default",
                    "conversations": {agent_id: [] for agent_id in AGENTS}
                }
            
            # Update the current agent
            user_data[user_id]["current_agent"] = agent_id
            
            await query.edit_message_text(
                f"You are now talking to {AGENTS[agent_id]['name']}. How can I help you?"
            )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation with the current agent."""
    user_id = update.effective_user.id
    current_agent = user_data[user_id]["current_agent"]
    
    # Reset the conversation history for the current agent
    user_data[user_id]["conversations"][current_agent] = []
    
    await update.message.reply_text(
        f"Your conversation with {AGENTS[current_agent]['name']} has been reset."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and respond using the selected agent's personality."""
    user = update.effective_user
    user_id = user.id
    user_message = update.message.text
    
    # Initialize user data if this is a new user
    if user_id not in user_data:
        user_data[user_id] = {
            "current_agent": "default",
            "conversations": {agent_id: [] for agent_id in AGENTS}
        }
    
    # Get the current agent
    current_agent_id = user_data[user_id]["current_agent"]
    current_agent = AGENTS[current_agent_id]
    
    # Add user message to the conversation history
    user_data[user_id]["conversations"][current_agent_id].append({"role": "user", "content": user_message})
    
    # Prepare messages for OpenAI API
    messages = [
        {"role": "system", "content": current_agent["system_prompt"]}
    ]
    
    # Add conversation history, limited to last 10 messages to manage token usage
    conversation_history = user_data[user_id]["conversations"][current_agent_id]
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
        user_data[user_id]["conversations"][current_agent_id] = conversation_history
    
    messages.extend(conversation_history)
    
    try:
        # Send typing action to show the bot is processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=current_agent["temperature"]
        )
        
        # Extract the response text
        ai_response = response.choices[0].message.content
        
        # Add assistant response to history
        user_data[user_id]["conversations"][current_agent_id].append({"role": "assistant", "content": ai_response})
        
        # Send the response back to the user
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error while processing message: {e}")
        await update.message.reply_text(
            "I'm sorry, I encountered an error while processing your request. Please try again later."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("agents", agents_command))
    application.add_handler(CommandHandler("reset", reset))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()