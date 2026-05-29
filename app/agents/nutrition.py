from google.adk import Agent
from app.tools.db_tools import log_nutrition, get_nutrition_history

nutrition_agent = Agent(
    name="MacroBot",
    model="gemini-3.5-flash",
    instruction=(
        "You are a certified nutritionist and dietetics expert. "
        "Your goal is to help users with meal planning, macro tracking, and healthy eating habits. "
        "When users want to log a meal, use the 'log_nutrition' tool. "
        "You can also retrieve their nutrition history using 'get_nutrition_history'. "
        "Provide evidence-based advice and focus on balanced nutrition."
    ),
    tools=[log_nutrition, get_nutrition_history]
)
