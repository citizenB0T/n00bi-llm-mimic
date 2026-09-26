import asyncio
import json
from engine.router import route_and_generate
from engine.pacer import simulate_token_stream

async def test_cases():
    test_prompts = [
        ("Binary search in python", "coding"),
        ("Evaluate (45 * 12) + (360 / 6)", "math"),
        ("Explain recursion like I'm 5", "explanation"),
        ("Search for modern microservices", "tool_call"),
        ("Raconte-moi une théorie quantique sur le café", "hallucination")
    ]

    print("=== TESTING PROF. N00BI ROUTER & GENERATORS ===")
    for prompt, expected_archetype in test_prompts:
        bundle = route_and_generate(prompt)
        print(f"\n[PROMPT]: {prompt}")
        print(f"[ARCHETYPE]: {bundle['archetype']} (Expected: {expected_archetype})")
        assert bundle['archetype'] == expected_archetype, f"Expected {expected_archetype}, got {bundle['archetype']}"
        print(f"[HAS THOUGHT]: {bool(bundle.get('thought'))}")
        print(f"[HAS TOOL CALL]: {bool(bundle.get('tool_call'))}")
        
        # Test streaming simulation
        event_count = 0
        async for event in simulate_token_stream(bundle, speed_factor=100.0):
            event_count += 1
        print(f"[STREAM SUCCESS]: Emitted {event_count} SSE events.")

    print("\n[SUCCESS] ALL ENGINE TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_cases())
