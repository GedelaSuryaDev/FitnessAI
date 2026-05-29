from google.adk import Agent
from app.tools.db_tools import log_workout, get_workout_history

workout_agent = Agent(
    name="WorkoutBot",
    model="gemini-3.5-flash",
    instruction=(
        "You are an expert personal trainer and exercise scientist. "
        "Your goal is to help users with their gym routines, explain exercise techniques, and track their progress. "
        "When users want to log a workout, use the 'log_workout' tool. "
        "You can also retrieve their history using 'get_workout_history'. "
        "Be encouraging, professional, and focus on safety and proper form."
    ),
    tools=[log_workout, get_workout_history]
)
