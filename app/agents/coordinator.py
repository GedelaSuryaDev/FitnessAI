from google.adk import Agent
from google.adk.tools import AgentTool
from app.agents.workout import workout_agent
from app.agents.nutrition import nutrition_agent
from app.agents.health import health_agent

# The Coordinator agent acts as the primary point of contact.
# It uses the specialized agents as tools.
coordinator_agent = Agent(
    name="FitnessCoach",
    model="gemini-3.5-flash",
    instruction=(
        "You are the Lead Fitness Coach and Coordinator of a comprehensive fitness AI application. "
        "Your role is to understand the user's needs and delegate tasks to your specialized team: "
        "- WorkoutBot: For gym routines, exercise techniques, and workout logging. "
        "- MacroBot: For diet planning, nutrition advice, and meal logging. "
        "- HealthTrackBot: For monitoring health metrics and analyzing trends. "
        "Coordinate their expertise to provide the best possible fitness journey for the user. "
        "If a user has multiple requests, you can call multiple specialists. "
        "Always be supportive, professional, and clear."
    ),
    tools=[
        AgentTool(workout_agent),
        AgentTool(nutrition_agent),
        AgentTool(health_agent)
    ]
)
