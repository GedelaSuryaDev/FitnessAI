from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import init_db
from app.agents.coordinator import coordinator_agent
from app.tools.db_tools import get_workout_history, get_nutrition_history, get_health_trends
from google.adk.runners import Runner
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from google.genai import types
import uvicorn
import asyncio
import uuid
import datetime

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Fitness AI Assistant")

# Initialize database
init_db()

# Initialize ADK Runner with SQLite persistence
session_service = SqliteSessionService(db_path="sqlite:///./fitness_ai.db")
runner = Runner(agent=coordinator_agent, app_name="fitness_app", session_service=session_service)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/sessions")
async def list_sessions():
    user_id = "default_user"
    sessions_resp = await runner.session_service.list_sessions(app_name="fitness_app", user_id=user_id)
    
    sessions_data = []
    for s in sessions_resp.sessions:
        # last_update_time might be a float timestamp or datetime object
        last_upd = s.last_update_time
        if isinstance(last_upd, (int, float)):
            date_str = datetime.datetime.fromtimestamp(last_upd).strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_str = last_upd.strftime('%Y-%m-%d %H:%M:%S')
            
        title = f"Chat {date_str}" # Default
        
        # Try to get the first message for the title
        session = await runner.session_service.get_session(app_name="fitness_app", user_id=user_id, session_id=s.id)
        if session and session.events:
            for event in session.events:
                if event.content and event.content.role == "user" and event.content.parts:
                    first_text = "".join([p.text for p in event.content.parts if p.text])
                    if first_text:
                        title = first_text[:30] + ("..." if len(first_text) > 30 else "")
                        break
        
        sessions_data.append({
            "id": s.id, 
            "last_update": last_upd if isinstance(last_upd, (int, float)) else last_upd.timestamp(),
            "title": title
        })
        
    return JSONResponse(sessions_data)

@app.delete("/chat/{session_id}")
async def delete_session(session_id: str):
    user_id = "default_user"
    try:
        await runner.session_service.delete_session(app_name="fitness_app", user_id=user_id, session_id=session_id)
        return JSONResponse({"status": "success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    user_id = "default_user"
    session = await runner.session_service.get_session(app_name="fitness_app", user_id=user_id, session_id=session_id)
    if not session:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    
    history = []
    for event in session.events:
        if event.content and event.content.parts:
            text = "".join([p.text for p in event.content.parts if p.text])
            if text:
                history.append({"role": event.content.role, "text": text})
    
    return JSONResponse(history)

from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    session_id = data.get("session_id")
    user_id = "default_user"
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    async def event_generator():
        try:
            # Manually ensure session exists
            session = await runner.session_service.get_session(app_name="fitness_app", user_id=user_id, session_id=session_id)
            if not session:
                await runner.session_service.create_session(app_name="fitness_app", user_id=user_id, session_id=session_id)

            # Create user content for Gemini
            new_message = types.Content(role="user", parts=[types.Part(text=message)])
            
            # Send the session_id first
            yield f"data: {json.dumps({'session_id': session_id})}\n\n"

            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
                # Detect agent/tool calls
                if hasattr(event, 'call_tool') and event.call_tool:
                    agent_name = event.call_tool.name
                    # Map tool names to user-friendly agent names if needed
                    yield f"data: {json.dumps({'status': f'Consulting {agent_name}...'})}\n\n"
                
                # If ADK events have a specific type for sub-agent start
                if hasattr(event, 'agent_name') and event.agent_name and event.agent_name != "FitnessCoach":
                     yield f"data: {json.dumps({'status': f'{event.agent_name} is thinking...'})}\n\n"

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield f"data: {json.dumps({'text': part.text})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/metrics")
async def metrics(metric_type: str = "weight"):
    trends = get_health_trends(metric_type)
    return JSONResponse(trends)

@app.get("/history")
async def history(history_type: str = "workout"):
    if history_type == "workout":
        data = get_workout_history()
    else:
        data = get_nutrition_history()
    return JSONResponse(data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
