import asyncio
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from engine.router import route_and_generate
from engine.pacer import simulate_token_stream
from engine.scenario_engine import scenario_manager

app = FastAPI(title="n00bi Engine", version="1.0.0")

# Enable CORS for open developer tooling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Track cumulative simulated savings
CUMULATIVE_STATS = {
    "requests_served": 0,
    "tokens_generated": 0,
    "vram_saved_gb": 0.0,
    "carbon_saved_grams": 0.0,
    "start_timestamp": time.time()
}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    speed: Optional[float] = 1.0
    scenario_id: Optional[str] = None
    session_id: Optional[str] = None

class ScenarioStartRequest(BaseModel):
    scenario_id: str
    session_id: str
    speed: Optional[float] = 1.0

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    return FileResponse(index_file)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC_DIR / "favicon.ico")

@app.get("/api/scenarios")
async def get_scenarios():
    return {"scenarios": scenario_manager.list_scenarios()}

@app.post("/api/scenario/start")
async def start_scenario(payload: ScenarioStartRequest):
    speed = payload.speed or 1.0
    bundle = scenario_manager.get_initial_turn(payload.session_id, payload.scenario_id)
    
    CUMULATIVE_STATS["requests_served"] += 1

    async def event_generator():
        async for sse_event in simulate_token_stream(bundle, speed_factor=speed):
            if sse_event["event"] == "metrics":
                data = json.loads(sse_event["data"])
                CUMULATIVE_STATS["tokens_generated"] += data.get("total_tokens", 0)
                CUMULATIVE_STATS["vram_saved_gb"] += data.get("vram_saved_gb", 80.0)
                CUMULATIVE_STATS["carbon_saved_grams"] += data.get("carbon_saved_grams", 0.0)
            yield sse_event

    return EventSourceResponse(event_generator())

@app.get("/api/stats")
async def get_stats():
    uptime_sec = round(time.time() - CUMULATIVE_STATS["start_timestamp"], 1)
    return {
        **CUMULATIVE_STATS,
        "uptime_seconds": uptime_sec,
        "cost_saved_usd": round(CUMULATIVE_STATS["tokens_generated"] * 0.00003, 4)
    }

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    user_prompt = payload.messages[-1].content if payload.messages else "Hello"
    speed = payload.speed or 1.0
    scenario_id = payload.scenario_id
    session_id = payload.session_id or "default_session"

    # Unified flow: All messages go through scenario_manager (with hybrid technical response support)
    scen_id = scenario_id if (scenario_id and scenario_id not in ("none", "free_mode")) else "evaluation_turing"
    bundle = scenario_manager.process_turn(session_id, user_prompt, scen_id)

    CUMULATIVE_STATS["requests_served"] += 1

    async def event_generator():
        async for sse_event in simulate_token_stream(bundle, speed_factor=speed):
            # Update cumulative stats when metrics event is reached
            if sse_event["event"] == "metrics":
                data = json.loads(sse_event["data"])
                CUMULATIVE_STATS["tokens_generated"] += data.get("total_tokens", 0)
                CUMULATIVE_STATS["vram_saved_gb"] += data.get("vram_saved_gb", 80.0)
                CUMULATIVE_STATS["carbon_saved_grams"] += data.get("carbon_saved_grams", 0.0)
            yield sse_event

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
