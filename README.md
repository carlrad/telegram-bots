# Telegram AI Agents Bot

A Telegram bot that provides access to multiple AI agents, each with specialized capabilities:

- **Assistant**: A general-purpose helpful assistant
- **Chef Gordon**: A personalized meal planner for family dinners
- **Fitness Coach Alex**: A fitness and nutrition expert
- **Dev Maya**: A programming and technical expert

## Features

- Multiple AI agents with different specialties
- Personalized meal planning with Chef Gordon
- Fitness and nutrition guidance
- Programming and technical assistance
- Easy agent switching through Telegram commands

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-bots.git
cd telegram-bots
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

5. Run the bot:
```bash
python main.py
```

## Usage

- `/start` - Start the bot
- `/help` - Show available commands
- `/agents` - Switch between different AI agents
- `/reset` - Reset the conversation with the current agent
- `/mealplan` - Generate a personalized meal plan (when using Chef Gordon)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 