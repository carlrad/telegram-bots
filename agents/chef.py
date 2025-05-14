"""
Chef Gordon agent implementation as a family meal planner for evening meals.

This agent helps busy families create personalized, diverse weekly dinner plans 
with healthy, balanced, seasonal recipes that can be prepared in 40 minutes or less.
"""

from agents.base import Agent
import json
from datetime import datetime, timedelta

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
4. Maintain culinary diversity and excitement in meal planning""",
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
        # Merge provided preferences with stored user preferences
        all_preferences = list(set(
            (preferences or []) + 
            self.user_profile['preferred_cuisines']
        ))
        
        # Merge provided restrictions with stored restrictions
        all_restrictions = list(set(
            (restrictions or []) + 
            self.user_profile['dietary_restrictions']
        ))
        
        # Incorporate user inspiration
        inspiration_context = ""
        if user_inspiration:
            if 'ingredient' in user_inspiration:
                inspiration_context += f"Incorporate {user_inspiration['ingredient']} into at least one meal. "
            if 'chef' in user_inspiration:
                inspiration_context += f"Draw inspiration from {user_inspiration['chef']}'s cooking style. "
        
        # Additional personalization context
        personalization_context = self.get_personalization_context()
        
        # Seasonal and culinary context (from existing methods)
        current_season, seasonal_ingredients = self.get_current_season()
        
        # Construct comprehensive prompt
        comprehensive_prompt = f"""
Create a highly personalized 5-day weekday dinner plan with the following considerations:

PERSONALIZATION CONTEXT:
{personalization_context}

USER INSPIRATION:
{inspiration_context}

SEASONAL CONSIDERATIONS:
Current season: {current_season}
Seasonal ingredients to feature: {', '.join(seasonal_ingredients[:5])}

GENERAL REQUIREMENTS:
- 5 unique, diverse dinner recipes
- Maximum 40 minutes preparation time per meal
- Avoid recently made meals and cuisines
- Incorporate seasonal ingredients
- Meet dietary needs and preferences
"""
        
        # Generate meal plan using LLM
        # Note: Actual LLM call would be implemented in the bot's message handler
        meal_plan = {
            "weekly_plan": {},
            "shopping_list": {},
            "recipes": {}
        }
        
        # Record this week's meals to prevent immediate repetition
        self.record_meal_history(meal_plan.get('weekly_plan', []))
        
        return meal_plan
    
    def suggest_chef_inspirations(self):
        """
        Provide a list of renowned chefs for meal planning inspiration.
        
        Returns:
            list: Suggested chefs with their culinary specialties
        """
        return [
            {"name": "Jamie Oliver", "cuisine": "Mediterranean, British", "specialty": "Fresh, simple meals"},
            {"name": "Ottolenghi", "cuisine": "Middle Eastern, Vegetarian", "specialty": "Vegetable-forward, spice-rich dishes"},
            {"name": "Rick Stein", "cuisine": "Seafood, International", "specialty": "Coastal and international cuisines"},
            {"name": "Massimo Bottura", "cuisine": "Italian", "specialty": "Modern, innovative Italian"},
            {"name": "David Chang", "cuisine": "Asian Fusion", "specialty": "Modern Asian cuisine"},
            {"name": "Dominique Crenn", "cuisine": "French", "specialty": "Artistic, progressive French"},
            {"name": "Yotam Ottolenghi", "cuisine": "Middle Eastern, Vegetarian", "specialty": "Vegetable-centric, spice-driven"},
            {"name": "Gordon Ramsay", "cuisine": "Modern European", "specialty": "Classic techniques, bold flavors"}
        ]