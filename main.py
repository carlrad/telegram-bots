"""
Main entry point for the Telegram bot application.
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

import config
from bot import start, help_command, agents_command, button_callback, reset, handle_message, meal_plan_command

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("agents", agents_command))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("mealplan", meal_plan_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()