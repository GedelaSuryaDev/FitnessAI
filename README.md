# Fitness AI Assistant

A comprehensive AI-powered fitness and nutrition coach that helps you track your workouts, monitor your nutrition, and provides personalized health advice using Gemini AI.

## Features

- **AI Chat Coach**: Get personalized advice on workouts, nutrition, and health trends.
- **Real-time Agent Tracking**: See which specialized agent (**WorkoutBot**, **MacroBot**, or **HealthTrackBot**) is currently processing your request.
- **Streaming Responses**: AI responses appear word-by-word in real-time for a faster, more interactive experience.
- **Dynamic Chat Management**:
    - Chats are automatically named based on your first question for easy identification.
    - Delete individual chat sessions from your history.
    - Start new sessions at any time.
- **Progress Dashboard**: Visualize your weight, heart rate, and sleep trends over time using interactive charts.
- **Activity Logs**: Keep track of your workout history and nutrition logs in one place.

## Project Structure

```text
/home/suryahack1/
├── app/
│   ├── main.py              # FastAPI server (Streaming enabled)
│   ├── database.py          # Database initialization and connection
│   ├── models.py            # SQLAlchemy database models
│   ├── agents/              # AI agent logic (Coordinator, Health, Nutrition, Workout)
│   ├── static/              # Frontend files
│   │   ├── index.html       # Main application page
│   │   ├── css/style.css    # Application styling & animations
│   │   └── js/app.js        # Frontend logic (Streaming & status handling)
│   └── tools/               # Helper tools for database access
├── fitness_ai.db            # SQLite database
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.12+
- A Google Cloud Project with Gemini API access (configured via `.env`)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file (e.g., `GOOGLE_API_KEY`).

### Running the App

Start the application using `uvicorn`:
```bash
uvicorn app.main:app --reload
```
The application will be available at `http://127.0.0.1:8000`.

## Recent Updates

- **Real-time Agent Status**: Added a pulsing indicator in the UI to show which specialized agent is working on the user's request.
- **Streaming AI Response**: Implemented FastAPI `StreamingResponse` and frontend `ReadableStream` for real-time text generation.
- **Improved Chat List**: Replaced generic timestamps with descriptive titles derived from user questions.
- **Delete Functionality**: Added the ability to remove old chat sessions from the sidebar.
- **Sleek UI**: Enhanced the sidebar and chat area with better status visibility and interactive elements.
