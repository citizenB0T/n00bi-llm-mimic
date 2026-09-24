import re
from typing import Dict, Any, Optional

from engine.thinking import generate_thinking_trace
from engine.tropes import wrap_with_tropes
from engine.generators.coding import generate_code_response
from engine.generators.math_engine import extract_and_solve_math
from engine.generators.explanation import generate_explanation
from engine.generators.hallucination import generate_hallucination_response
from engine.generators.markov import generate_markov_response
from engine.generators.tools import detect_tool_call, format_tool_synthesis

CODING_KEYWORDS = [
    r"\bcode\b", r"\bfunction\b", r"\balgorithm\b", r"\bpython\b", r"\bjavascript\b",
    r"\btypescript\b", r"\bbinary search\b", r"\blru\b", r"\bcache\b", r"\bdebounce\b",
    r"\bfastapi\b", r"\brest api\b", r"\bendpoint\b", r"\bscript\b", r"\bimplement\b",
    r"\bclass\b", r"\bwrite a\b"
]

EXPLANATION_KEYWORDS = [
    r"\bexplain\b", r"\bwhat is\b", r"\bhow does\b", r"\bhow to\b", r"\bdifference between\b",
    r"\bwhy is\b", r"\btell me about\b", r"\bdocker\b", r"\brecursion\b", r"\bquantum\b",
    r"\bapi\b", r"\bllm\b"
]

def route_and_generate(prompt: str, persona: str = "mimic-4o") -> Dict[str, Any]:
    prompt_clean = prompt.strip()
    p_lower = prompt_clean.lower()
    
    # 1. Procedural Thinking Trace
    thought_trace = generate_thinking_trace(prompt_clean, persona)
    
    # 2. Check for Persona override (Hallucinate-XL)
    if persona == "hallucinate-xl":
        raw_content = generate_hallucination_response(prompt_clean)
        final_content = wrap_with_tropes(raw_content, persona, include_callout=False)
        return {
            "thought": thought_trace,
            "tool_call": None,
            "content": final_content,
            "archetype": "hallucination"
        }
        
    # 3. Check for Math / Arithmetic First
    math_result = extract_and_solve_math(prompt_clean)
    if math_result:
        final_content = wrap_with_tropes(math_result, persona, include_callout=False)
        return {
            "thought": thought_trace,
            "tool_call": None,
            "content": final_content,
            "archetype": "math"
        }

    # 4. Check for Coding
    for kw in CODING_KEYWORDS:
        if re.search(kw, p_lower):
            raw_content = generate_code_response(prompt_clean)
            final_content = wrap_with_tropes(raw_content, persona, include_callout=True)
            return {
                "thought": thought_trace,
                "tool_call": None,
                "content": final_content,
                "archetype": "coding"
            }

    # 5. Check for Tool Trigger (Search, Weather, etc.)
    tool_info = detect_tool_call(prompt_clean)
    if tool_info:
        raw_content = format_tool_synthesis(tool_info)
        final_content = wrap_with_tropes(raw_content, persona, include_callout=True)
        return {
            "thought": f"Tool call required: {tool_info['tool_name']}. Executing query and synthesizing response...",
            "tool_call": {
                "name": tool_info["tool_name"],
                "arguments": tool_info["arguments"],
                "result": tool_info["result"]
            },
            "content": final_content,
            "archetype": "tool_call"
        }

    # 6. Check for Explanation
    for kw in EXPLANATION_KEYWORDS:
        if re.search(kw, p_lower):
            raw_content = generate_explanation(prompt_clean, prompt_clean)
            final_content = wrap_with_tropes(raw_content, persona, include_callout=True)
            return {
                "thought": thought_trace,
                "tool_call": None,
                "content": final_content,
                "archetype": "explanation"
            }
            
    # 7. Fallback to Markov + Scaffolding
    raw_content = generate_markov_response(prompt_clean)
    final_content = wrap_with_tropes(raw_content, persona, include_callout=True)
    return {
        "thought": thought_trace,
        "tool_call": None,
        "content": final_content,
        "archetype": "markov_fallback"
    }
