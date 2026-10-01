import asyncio
import json
import random
import time
from typing import AsyncGenerator, Dict, Any

async def simulate_token_stream(
    response_bundle: Dict[str, Any],
    speed_factor: float = 1.0,
    no_delay: bool = False
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Yields Server-Sent Event (SSE) dictionaries formatted as:
    {'event': '<event_type>', 'data': '<json_string>'}
    """
    start_time = time.time()
    total_tokens = 0
    is_instant = no_delay or (speed_factor >= 100.0)

    thought = response_bundle.get("thought")
    tool_call = response_bundle.get("tool_call")
    content = response_bundle.get("content", "")

    # 1. Stream Thought (if present)
    if thought:
        yield {
            "event": "thought_start",
            "data": json.dumps({"status": "thinking"})
        }
        if not is_instant:
            await asyncio.sleep(0.15)

        # Split thought into small word chunks
        thought_words = thought.split(" ")
        for i, word in enumerate(thought_words):
            chunk = word if i == 0 else " " + word
            total_tokens += max(1, len(chunk) // 4)
            yield {
                "event": "thought",
                "data": json.dumps({"delta": chunk})
            }
            # Reasoning tokens stream faster (~8-15ms)
            if not is_instant:
                await asyncio.sleep(random.uniform(0.008, 0.018) / speed_factor)

        yield {
            "event": "thought_end",
            "data": json.dumps({"status": "completed"})
        }
        if not is_instant:
            await asyncio.sleep(0.2)

    # 2. Simulate Tool Call (if present)
    if tool_call:
        yield {
            "event": "tool_call",
            "data": json.dumps({
                "status": "executing",
                "name": tool_call["name"],
                "arguments": tool_call["arguments"]
            })
        }
        # Simulate network latency for API/search call
        if not is_instant:
            await asyncio.sleep(0.6 / speed_factor)

        yield {
            "event": "tool_result",
            "data": json.dumps({
                "status": "success",
                "name": tool_call["name"],
                "result": tool_call["result"]
            })
        }
        if not is_instant:
            await asyncio.sleep(0.3 / speed_factor)

    # 3. Stream Response Content
    yield {
        "event": "content_start",
        "data": json.dumps({"status": "generating"})
    }

    # Tokenize content by words and punctuation boundaries
    # This gives realistic token chunking
    tokens = []
    current = ""
    for char in content:
        current += char
        if char in (" ", "\n", ".", ",", ":", ";", "!", "?", "`"):
            tokens.append(current)
            current = ""
    if current:
        tokens.append(current)

    for token in tokens:
        total_tokens += max(1, len(token) // 4)
        yield {
            "event": "content",
            "data": json.dumps({"delta": token})
        }

        if not is_instant:
            # Dynamic pause calculation
            base_delay = random.uniform(0.015, 0.035) / speed_factor
            if token.endswith("\n\n"):
                base_delay += 0.08
            elif any(token.endswith(p) for p in (".", "!", "?")):
                base_delay += 0.05
            elif token.endswith("```"):
                base_delay += 0.1

            await asyncio.sleep(base_delay)

    # 4. Scenario State and Suggestions Events
    if "scenario_state" in response_bundle and response_bundle["scenario_state"]:
        yield {
            "event": "scenario_state",
            "data": json.dumps(response_bundle["scenario_state"])
        }

    if "suggestions" in response_bundle and response_bundle["suggestions"]:
        yield {
            "event": "suggestions",
            "data": json.dumps({"suggestions": response_bundle["suggestions"]})
        }

    # 5. Final Metrics Event
    elapsed = max(0.1, time.time() - start_time)
    tps = round(total_tokens / elapsed, 1)

    yield {
        "event": "metrics",
        "data": json.dumps({
            "total_tokens": total_tokens,
            "elapsed_seconds": round(elapsed, 2),
            "tokens_per_sec": tps,
            "vram_saved_gb": 80.0,
            "carbon_saved_grams": round(total_tokens * 0.00042, 5),
            "archetype": response_bundle.get("archetype", "general")
        })
    }

    # 6. Done Event
    yield {
        "event": "done",
        "data": json.dumps({"status": "finished"})
    }
