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

app = FastAPI(title="MimicLLM Engine", version="1.0.0")

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

# Models metadata
MODELS_CATALOG = [
    {
        "id": "mimic-4o",
        "name": "Mimic-4o-Omni",
        "badge": "Default",
        "description": "Fast, eager-to-please, structured lists, enthusiastic tone.",
        "icon": "zap",
        "vram": "0 GB (Saved 80 GB)"
    },
    {
        "id": "deepfake-r1",
        "name": "DeepFake-R1 (Reasoning)",
        "badge": "Reasoning",
        "description": "Extremely verbose self-reflective internal monologue before answer.",
        "icon": "brain",
        "vram": "0 GB (Saved 140 GB)"
    },
    {
        "id": "claude-haiku",
        "name": "Claude-3.9-Haiku-ish",
        "badge": "Nuanced",
        "description": "Thoughtful, ethical caveats, measured tone, refuses harmless prompts playfully.",
        "icon": "feather",
        "vram": "0 GB (Saved 70 GB)"
    },
    {
        "id": "hallucinate-xl",
        "name": "Hallucinate-XL",
        "badge": "Novelty",
        "description": "Speaks with absolute scientific authority citing made-up research papers.",
        "icon": "sparkles",
        "vram": "0 GB (Saved 320 GB)"
    }
]

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
    model: Optional[str] = "mimic-4o"
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

@app.get("/api/models")
async def get_models():
    return {"models": MODELS_CATALOG}

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
    model = payload.model or "mimic-4o"
    speed = payload.speed or 1.0
    scenario_id = payload.scenario_id
    session_id = payload.session_id or "default_session"

    # Route and synthesize response
    if scenario_id and scenario_id != "none" and scenario_id != "free_mode":
        bundle = scenario_manager.process_turn(session_id, user_prompt, scenario_id)
    else:
        bundle = route_and_generate(user_prompt, persona=model)

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

# OpenAI API Compatible Endpoint (/v1/chat/completions)
@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    model = data.get("model", "mimic-4o")
    stream = data.get("stream", False)
    
    user_prompt = messages[-1].get("content", "") if messages else "Hello"
    bundle = route_and_generate(user_prompt, persona=model)
    created_ts = int(time.time())

    if stream:
        async def openai_stream():
            async for sse_event in simulate_token_stream(bundle):
                if sse_event["event"] == "content":
                    chunk_data = json.loads(sse_event["data"])
                    payload = {
                        "id": f"chatcmpl-mimic-{created_ts}",
                        "object": "chat.completion.chunk",
                        "created": created_ts,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": chunk_data["delta"]},
                                "finish_reason": None
                            }
                        ]
                    }
                    yield {"data": json.dumps(payload)}
            
            # Send finish reason chunk
            finish_payload = {
                "id": f"chatcmpl-mimic-{created_ts}",
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield {"data": json.dumps(finish_payload)}
            yield {"data": "[DONE]"}

        return EventSourceResponse(openai_stream())
    else:
        return {
            "id": f"chatcmpl-mimic-{created_ts}",
            "object": "chat.completion",
            "created": created_ts,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": bundle["content"]
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_prompt) // 4,
                "completion_tokens": len(bundle["content"]) // 4,
                "total_tokens": (len(user_prompt) + len(bundle["content"])) // 4
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
