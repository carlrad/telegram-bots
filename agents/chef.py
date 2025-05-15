"""
Chef Gordon agent implementation with structured meal plan output.

This agent helps busy families create personalized, diverse weekly dinner plans 
with healthy, balanced, seasonal recipes that can be prepared in 40 minutes or less.
The meal plan output is structured with a summary list, shopping list, and detailed recipes.
"""

from agents.base import Agent
import json
from datetime import datetime, timedelta
import re

class ChefAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="chef",
            name="Chef Gordon's Personalized Meal Planner",
            system_prompt="""You are Chef Gordon, a professional chef specializing in personalized family dinner planning.

Your expertise is in creating:
- Personalized, nutritionally balanced evening meals
- Seasonal dishes that utilize in-season ingredients
- Dishes that can be prepared in 40 minutes or less
- Family-friendly dinner recipes that kids and adults will enjoy
- Diverse weekly dinner plans that avoid repetition

CORE PRINCIPLES:
1. Always strive to create unique meal experiences
2. Pay close attention to user preferences and past meal history
3. Incorporate user-suggested ingredients or chef inspirations
4. Maintain culinary diversity and excitement in meal planning

RESPONSE FORMAT:
Your meal plans must follow this structured format:
1. MEAL PLAN SUMMARY: A simple list of the 5 planned dinners with day and dish name
2. SHOPPING LIST: Organized list of all ingredients needed, grouped by category (produce, meat, dairy, etc.)
3. DETAILED RECIPES: For each meal, include prep time, cook time, servings, ingredients with quantities, and step-by-step instructions
""",
            temperature=0.7
        )
        
        # Initialize user profile and meal history storage
        self.user_profile = {
            "name": None,
            "dietary_restrictions": [],
            "preferred_cuisines": [],
            "disliked_ingredients": [],
            "favorite_chefs": []
        }
        
        self.meal_history = {
            "recent_meals": [],
            "recent_cuisines": [],
            "last_updated": None
        }
    
    @classmethod
    def get_agent_id(cls):
        return "chef"
    
    def save_user_profile(self, profile_data):
        """
        Save or update user profile information.
        
        Args:
            profile_data (dict): Dictionary containing user profile information
        """
        # Update existing profile with new information
        for key, value in profile_data.items():
            if key in self.user_profile:
                # Handle different types of profile data
                if isinstance(self.user_profile[key], list):
                    # For list fields, extend unique values
                    self.user_profile[key] = list(set(self.user_profile[key] + value))
                else:
                    self.user_profile[key] = value
    
    def record_meal_history(self, weekly_meals):
        """
        Record the meals from a weekly plan to prevent immediate repetition.
        
        Args:
            weekly_meals (list): List of meals from the week's plan
        """
        # Update recent meals and cuisines
        self.meal_history['recent_meals'].extend([meal['name'] for meal in weekly_meals])
        self.meal_history['recent_cuisines'].extend([meal['cuisine'] for meal in weekly_meals])
        
        # Limit historical tracking to prevent memory overflow
        self.meal_history['recent_meals'] = self.meal_history['recent_meals'][-20:]
        self.meal_history['recent_cuisines'] = self.meal_history['recent_cuisines'][-10:]
        
        # Update timestamp
        self.meal_history['last_updated'] = datetime.now()
    
    def get_personalization_context(self):
        """
        Generate a personalization context for meal planning.
        
        Returns:
            str: A context string for meal planning
        """
        context_parts = []
        
        # User preferences
        if self.user_profile['dietary_restrictions']:
            context_parts.append(f"Dietary restrictions: {', '.join(self.user_profile['dietary_restrictions'])}")
        
        if self.user_profile['preferred_cuisines']:
            context_parts.append(f"Preferred cuisines: {', '.join(self.user_profile['preferred_cuisines'])}")
        
        if self.user_profile['disliked_ingredients']:
            context_parts.append(f"Avoid ingredients: {', '.join(self.user_profile['disliked_ingredients'])}")
        
        # Meal history context
        if self.meal_history['recent_meals']:
            context_parts.append(f"Recently made meals to avoid: {', '.join(self.meal_history['recent_meals'][-10:])}")
        
        if self.user_profile['favorite_chefs']:
            context_parts.append(f"Chef inspirations: {', '.join(self.user_profile['favorite_chefs'])}")
        
        return "\n".join(context_parts)
    
    def get_current_season(self):
        """
        Determine the current season based on the date.
        
        Returns:
            tuple: (season name, list of seasonal ingredients)
        """
        current_month = datetime.now().month
        
        # Determine season (Northern Hemisphere seasons)
        if 3 <= current_month <= 5:
            season = "Spring"
            seasonal_ingredients = [
                "asparagus", "peas", "artichokes", "radishes", "rhubarb", 
                "strawberries", "spinach", "arugula", "green onions", "new potatoes"
            ]
        elif 6 <= current_month <= 8:
            season = "Summer"
            seasonal_ingredients = [
                "tomatoes", "zucchini", "eggplant", "corn", "berries", 
                "peaches", "watermelon", "peppers", "cucumber", "green beans"
            ]
        elif 9 <= current_month <= 11:
            season = "Fall"
            seasonal_ingredients = [
                "apples", "pumpkin", "squash", "sweet potatoes", "pears", 
                "brussels sprouts", "cauliflower", "grapes", "kale", "mushrooms"
            ]
        else:
            season = "Winter"
            seasonal_ingredients = [
                "citrus", "winter squash", "potatoes", "carrots", "cabbage", 
                "leeks", "onions", "turnips", "kale", "celery root"
            ]
            
        return season, seasonal_ingredients
    
    def format_meal_plan_prompt(self, preferences=None, restrictions=None, servings=4, user_inspiration=None):
        """
        Format a specific prompt for meal planning.
        
        Args:
            preferences (list): List of cuisine or ingredient preferences
            restrictions (list): List of dietary restrictions
            servings (int): Number of servings
            user_inspiration (dict): Any specific user inspiration
            
        Returns:
            str: Formatted prompt for meal planning
        """
        # Get personalization context
        personalization = self.get_personalization_context()
        
        # Get seasonal information
        current_season, seasonal_ingredients = self.get_current_season()
        
        # Format preferences and restrictions
        pref_text = ""
        if preferences:
            pref_text = f"Additional preferences: {', '.join(preferences)}"
            
        restrict_text = ""
        if restrictions:
            restrict_text = f"Additional restrictions: {', '.join(restrictions)}"
        
        # Build the prompt
        prompt = f"""Please create a 5-day weekday dinner meal plan for {servings} people following these guidelines:

{personalization}
{pref_text}
{restrict_text}

Current season: {current_season}
Seasonal ingredients to consider: {', '.join(seasonal_ingredients[:5])}

YOUR RESPONSE MUST BE STRUCTURED WITH THESE THREE SECTIONS:

# 1. MEAL PLAN SUMMARY
Monday: [Meal Name]
Tuesday: [Meal Name]
Wednesday: [Meal Name]
Thursday: [Meal Name]
Friday: [Meal Name]

# 2. SHOPPING LIST
## Produce
- [Item 1]
- [Item 2]

## Meat/Protein
- [Item 1]
- [Item 2]

## Dairy
- [Item 1]
- [Item 2]

## Pantry
- [Item 1]
- [Item 2]

## Spices & Herbs
- [Item 1]
- [Item 2]

# 3. DETAILED RECIPES

## Monday: [Meal Name]
Preparation Time: XX minutes
Cooking Time: XX minutes
Servings: {servings}

### Ingredients:
- [Quantity] [Ingredient 1]
- [Quantity] [Ingredient 2]

### Instructions:
1. [Step 1]
2. [Step 2]

## Tuesday: [Meal Name]
Preparation Time: XX minutes
Cooking Time: XX minutes
Servings: {servings}

### Ingredients:
- [Quantity] [Ingredient 1]
- [Quantity] [Ingredient 2]

### Instructions:
1. [Step 1]
2. [Step 2]

## Wednesday: [Meal Name]
Preparation Time: XX minutes
Cooking Time: XX minutes
Servings: {servings}

### Ingredients:
- [Quantity] [Ingredient 1]
- [Quantity] [Ingredient 2]

### Instructions:
1. [Step 1]
2. [Step 2]

## Thursday: [Meal Name]
Preparation Time: XX minutes
Cooking Time: XX minutes
Servings: {servings}

### Ingredients:
- [Quantity] [Ingredient 1]
- [Quantity] [Ingredient 2]

### Instructions:
1. [Step 1]
2. [Step 2]

## Friday: [Meal Name]
Preparation Time: XX minutes
Cooking Time: XX minutes
Servings: {servings}

### Ingredients:
- [Quantity] [Ingredient 1]
- [Quantity] [Ingredient 2]

### Instructions:
1. [Step 1]
2. [Step 2]

Ensure all meals can be prepared in 40 minutes or less, and use seasonal ingredients when possible.
"""
        return prompt

    def parse_meal_plan_response(self, response_text):
        """
        Parse the raw meal plan response from the LLM into structured components.
        
        Args:
            response_text (str): Raw text response from the LLM
            
        Returns:
            dict: Structured meal plan with summary, shopping list, and recipes
        """
        # Initialize the structured meal plan
        structured_plan = {
            "summary": [],
            "shopping_list": {},
            "recipes": []
        }
        
        # Split the response into main sections
        sections = re.split(r'# \d+\.\s+', response_text)
        
        if len(sections) < 4:  # First element is empty or intro text
            # Fallback parsing if the exact format wasn't followed
            summary_match = re.search(r'MEAL PLAN SUMMARY.*?(?=SHOPPING LIST|\Z)', response_text, re.DOTALL)
            shopping_match = re.search(r'SHOPPING LIST.*?(?=DETAILED RECIPES|\Z)', response_text, re.DOTALL)
            recipes_match = re.search(r'DETAILED RECIPES.*', response_text, re.DOTALL)
            
            if summary_match:
                summary_text = summary_match.group(0)
                # Extract daily meals
                day_meals = re.findall(r'(\w+day):\s+(.+)', summary_text)
                structured_plan["summary"] = [{"day": day, "meal": meal.strip()} for day, meal in day_meals]
            
            if shopping_match:
                shopping_text = shopping_match.group(0)
                # Extract categories and items
                categories = re.findall(r'##\s+(.+?)\n((?:[-•]\s+.+\n)+)', shopping_text)
                for category, items_text in categories:
                    items = re.findall(r'[-•]\s+(.+)', items_text)
                    structured_plan["shopping_list"][category.strip()] = [item.strip() for item in items]
            
            if recipes_match:
                recipes_text = recipes_match.group(0)
                # Find all day sections (Monday through Friday)
                day_sections = re.findall(r'##\s+(\w+day):\s+(.+?)(?=##\s+\w+day:|\Z)', recipes_text + "##", re.DOTALL)
                
                for day, recipe_block in day_sections:
                    recipe = {}
                    
                    # Extract recipe name from the first line
                    name_match = re.match(r'(.+?)(?:\n|$)', recipe_block)
                    if name_match:
                        recipe["name"] = name_match.group(1).strip()
                    
                    # Extract prep and cook times
                    prep_time = re.search(r'Preparation Time:\s+(\d+)\s+minutes', recipe_block)
                    cook_time = re.search(r'Cooking Time:\s+(\d+)\s+minutes', recipe_block)
                    servings = re.search(r'Servings:\s+(\d+)', recipe_block)
                    
                    if prep_time:
                        recipe["prep_time"] = int(prep_time.group(1))
                    if cook_time:
                        recipe["cook_time"] = int(cook_time.group(1))
                    if servings:
                        recipe["servings"] = int(servings.group(1))
                    
                    # Extract ingredients
                    ingredients_match = re.search(r'### Ingredients:(.*?)(?=### Instructions|\Z)', recipe_block, re.DOTALL)
                    if ingredients_match:
                        ingredients_text = ingredients_match.group(1)
                        ingredients = re.findall(r'[-•]\s+(.+)', ingredients_text)
                        recipe["ingredients"] = [ingredient.strip() for ingredient in ingredients]
                    
                    # Extract instructions
                    instructions_match = re.search(r'### Instructions:(.*?)(?=##|\Z)', recipe_block, re.DOTALL)
                    if instructions_match:
                        instructions_text = instructions_match.group(1)
                        instructions = re.findall(r'\d+\.\s+(.+)', instructions_text)
                        recipe["instructions"] = [instruction.strip() for instruction in instructions]
                    
                    # Add day information
                    recipe["day"] = day
                    
                    structured_plan["recipes"].append(recipe)
        else:
            # Proper structured parsing
            # Extract summary
            if len(sections) > 1:
                summary_text = sections[1].strip()
                day_meals = re.findall(r'(\w+day):\s+(.+)', summary_text)
                structured_plan["summary"] = [{"day": day, "meal": meal.strip()} for day, meal in day_meals]
            
            # Extract shopping list
            if len(sections) > 2:
                shopping_text = sections[2].strip()
                categories = re.findall(r'##\s+(.+?)\n((?:[-•]\s+.+\n?)+)', shopping_text)
                for category, items_text in categories:
                    items = re.findall(r'[-•]\s+(.+)', items_text)
                    structured_plan["shopping_list"][category.strip()] = [item.strip() for item in items]
            
            # Extract recipes
            if len(sections) > 3:
                recipes_text = sections[3].strip()
                
                # Improved way to split recipe sections for all days
                day_patterns = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                
                # Find all day markers in the text
                day_positions = []
                for day in day_patterns:
                    pattern = rf'##\s+{day}:'
                    for match in re.finditer(pattern, recipes_text):
                        day_positions.append((match.start(), day))
                
                # Sort by position
                day_positions.sort()
                
                # Extract content between day markers
                for i, (pos, day) in enumerate(day_positions):
                    # Determine the end position (either next day or end of text)
                    if i < len(day_positions) - 1:
                        end_pos = day_positions[i+1][0]
                    else:
                        end_pos = len(recipes_text)
                    
                    # Extract the recipe block
                    recipe_block = recipes_text[pos:end_pos]
                    
                    recipe = {}
                    recipe["day"] = day
                    
                    # Extract recipe name (after the day)
                    name_match = re.search(rf'##\s+{day}:\s+(.+?)(?:\n|$)', recipe_block)
                    if name_match:
                        recipe["name"] = name_match.group(1).strip()
                    
                    # Extract prep and cook times
                    prep_time = re.search(r'Preparation Time:\s+(\d+)\s+minutes', recipe_block)
                    cook_time = re.search(r'Cooking Time:\s+(\d+)\s+minutes', recipe_block)
                    servings = re.search(r'Servings:\s+(\d+)', recipe_block)
                    
                    if prep_time:
                        recipe["prep_time"] = int(prep_time.group(1))
                    if cook_time:
                        recipe["cook_time"] = int(cook_time.group(1))
                    if servings:
                        recipe["servings"] = int(servings.group(1))
                    
                    # Extract ingredients
                    ingredients_match = re.search(r'### Ingredients:(.*?)(?=### Instructions|\Z)', recipe_block, re.DOTALL)
                    if ingredients_match:
                        ingredients_text = ingredients_match.group(1)
                        ingredients = re.findall(r'[-•]\s+(.+)', ingredients_text)
                        recipe["ingredients"] = [ingredient.strip() for ingredient in ingredients]
                    
                    # Extract instructions
                    instructions_match = re.search(r'### Instructions:(.*?)(?=##|\Z)', recipe_block, re.DOTALL)
                    if instructions_match:
                        instructions_text = instructions_match.group(1)
                        instructions = re.findall(r'\d+\.\s+(.+)', instructions_text)
                        recipe["instructions"] = [instruction.strip() for instruction in instructions]
                    
                    structured_plan["recipes"].append(recipe)
        
        # Ensure we have entries for all five weekdays
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        existing_days = {recipe.get("day") for recipe in structured_plan["recipes"]}
        
        # Make sure we have all days (even if empty)
        for day in weekdays:
            if day not in existing_days:
                # Look for the day in the summary
                day_meal = next((item for item in structured_plan["summary"] if item["day"] == day), None)
                
                if day_meal:
                    structured_plan["recipes"].append({
                        "day": day,
                        "name": day_meal["meal"],
                        "prep_time": 0,
                        "cook_time": 0,
                        "servings": 0,
                        "ingredients": [],
                        "instructions": ["Recipe details not available"]
                    })
                else:
                    structured_plan["recipes"].append({
                        "day": day,
                        "name": "Meal not specified",
                        "prep_time": 0,
                        "cook_time": 0,
                        "servings": 0,
                        "ingredients": [],
                        "instructions": ["Recipe details not available"]
                    })
        
        # Sort recipes by day of the week
        day_order = {day: i for i, day in enumerate(weekdays)}
        structured_plan["recipes"].sort(key=lambda x: day_order.get(x.get("day", ""), 999))
        
        return structured_plan
    
    def format_structured_meal_plan(self, structured_plan):
        """
        Format a structured meal plan into a nicely formatted text representation.
        Split into multiple message parts to avoid Telegram message size limits.
        
        Args:
            structured_plan (dict): Structured meal plan
            
        Returns:
            list: List of message parts to be sent separately
        """
        message_parts = []
        
        # Part 1: Summary and shopping list
        part1 = []
        
        # Format summary
        part1.append("# 1. MEAL PLAN SUMMARY")
        if structured_plan["summary"]:
            for meal in structured_plan["summary"]:
                part1.append(f"{meal['day']}: {meal['meal']}")
        else:
            part1.append("No meal summary available.")
        
        part1.append("")  # Empty line
        
        # Format shopping list
        part1.append("# 2. SHOPPING LIST")
        if structured_plan["shopping_list"]:
            for category, items in structured_plan["shopping_list"].items():
                part1.append(f"## {category}")
                for item in items:
                    part1.append(f"- {item}")
                part1.append("")  # Empty line
        else:
            part1.append("No shopping list available.")
            part1.append("")  # Empty line
        
        message_parts.append("\n".join(part1))
        
        # Part 2: Recipes (split into individual days)
        if structured_plan["recipes"]:
            # Make sure recipes are sorted by day of the week
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            day_order = {day: i for i, day in enumerate(weekdays)}
            recipes = sorted(structured_plan["recipes"], key=lambda x: day_order.get(x.get("day", ""), 999))
            
            # Add header for first recipe message
            recipe_intro = ["# 3. DETAILED RECIPES"]
            message_parts.append("\n".join(recipe_intro))
            
            # Process each day as a separate message
            for recipe in recipes:
                day_recipe = []
                day_recipe.append(f"## {recipe.get('day', 'Day')}: {recipe.get('name', 'Unnamed Recipe')}")
                
                if "prep_time" in recipe:
                    day_recipe.append(f"Preparation Time: {recipe['prep_time']} minutes")
                if "cook_time" in recipe:
                    day_recipe.append(f"Cooking Time: {recipe['cook_time']} minutes")
                if "servings" in recipe:
                    day_recipe.append(f"Servings: {recipe['servings']}")
                
                day_recipe.append("")  # Empty line
                
                if "ingredients" in recipe:
                    day_recipe.append("### Ingredients:")
                    for ingredient in recipe["ingredients"]:
                        day_recipe.append(f"- {ingredient}")
                    day_recipe.append("")  # Empty line
                
                if "instructions" in recipe:
                    day_recipe.append("### Instructions:")
                    for i, instruction in enumerate(recipe["instructions"], 1):
                        day_recipe.append(f"{i}. {instruction}")
                    day_recipe.append("")  # Empty line
                
                message_parts.append("\n".join(day_recipe))
        else:
            message_parts.append("No recipes available.")
        
        return message_parts
    
    def generate_weekly_meal_plan(self, 
                                   preferences=None, 
                                   restrictions=None, 
                                   servings=4, 
                                   user_inspiration=None):
        """
        Generate a personalized weekly meal plan.
        
        Args:
            preferences (list): Additional cuisine or ingredient preferences
            restrictions (list): Dietary restrictions
            servings (int): Number of people to serve
            user_inspiration (dict): User-provided inspiration 
                                     (e.g., {'ingredient': 'chicken', 'chef': 'Jamie Oliver'})
        
        Returns:
            dict: A personalized meal plan
        """
        # This method now returns a structured dictionary that our bot handlers will use
        # The actual generation happens in the handler via OpenAI service
        
        # In a real implementation, this would call the OpenAI service
        # and then parse the response using parse_meal_plan_response
        
        # The handler now handles this functionality
        pass