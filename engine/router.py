import re
from typing import Dict, Any, Optional

from engine.thinking import generate_thinking_trace
from engine.tropes import wrap_with_tropes, is_english
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
    r"\bwhy is\b", r"\btell me about\b", r"\bdocker\b", r"\brecursion\b", r"\bapi\b",
    r"\bllm\b", r"\bqu'est-ce\b", r"\bcomment\b", r"\bpourquoi\b", r"\bexplique\b",
    r"\bdifférence entre\b"
]

UNEXPECTED_KEYWORDS = [
    r"\bhallucin\w*", r"\binvente\b", r"\bthèse\b", r"\bpseudo[- ]science\b",
    r"\bquantique\b", r"\bquantum\b", r"\bcomplot\b", r"\bfake\b", r"\bbobard\b",
    r"\babsurde\b", r"\balien\b", r"\bperlimpinpin\b", r"\bvoyage dans le temps\b",
    r"\bcoffee\b", r"\bcafé quantique\b", r"\bsecret de l'univers\b"
]

def route_and_generate(prompt: str, persona: Optional[str] = None, *args, **kwargs) -> Dict[str, Any]:
    prompt_clean = prompt.strip()
    p_lower = prompt_clean.lower()
    is_en = is_english(prompt_clean)
    
    # 1. Procedural Thinking Trace (Prof. n00bi)
    thought_trace = generate_thinking_trace(prompt_clean)
    
    # 2. Check for Math / Arithmetic First
    math_result = extract_and_solve_math(prompt_clean)
    if math_result:
        final_content = wrap_with_tropes(math_result, include_callout=False, is_en=is_en)
        return {
            "thought": thought_trace,
            "tool_call": None,
            "content": final_content,
            "archetype": "math"
        }

    # 3. Check for Coding
    for kw in CODING_KEYWORDS:
        if re.search(kw, p_lower):
            raw_content = generate_code_response(prompt_clean)
            final_content = wrap_with_tropes(raw_content, include_callout=True, is_en=is_en)
            return {
                "thought": thought_trace,
                "tool_call": None,
                "content": final_content,
                "archetype": "coding"
            }

    # 4. Check for Tool Trigger (Search, Weather, etc.)
    tool_info = detect_tool_call(prompt_clean)
    if tool_info:
        raw_content = format_tool_synthesis(tool_info)
        final_content = wrap_with_tropes(raw_content, include_callout=True, is_en=is_en)
        return {
            "thought": f"Outil pédagogique requis : {tool_info['tool_name']}. Consultation des registres et synthèse didactique...",
            "tool_call": {
                "name": tool_info["tool_name"],
                "arguments": tool_info["arguments"],
                "result": tool_info["result"]
            },
            "content": final_content,
            "archetype": "tool_call"
        }

    # 5. Check for Unexpected / Out-of-syllabus queries (Hallucination case study)
    for kw in UNEXPECTED_KEYWORDS:
        if re.search(kw, p_lower):
            raw_content = generate_hallucination_response(prompt_clean)
            return {
                "thought": thought_trace,
                "tool_call": None,
                "content": raw_content,
                "archetype": "hallucination"
            }

    # 6. Check for Explanation
    for kw in EXPLANATION_KEYWORDS:
        if re.search(kw, p_lower):
            raw_content = generate_explanation(prompt_clean, prompt_clean)
            final_content = wrap_with_tropes(raw_content, include_callout=True, is_en=is_en)
            return {
                "thought": thought_trace,
                "tool_call": None,
                "content": final_content,
                "archetype": "explanation"
            }
            
    # 7. Fallback: Markov + Pedagogical Scaffolding
    raw_content = generate_markov_response(prompt_clean)
    final_content = wrap_with_tropes(raw_content, include_callout=True, is_en=is_en)
    return {
        "thought": thought_trace,
        "tool_call": None,
        "content": final_content,
        "archetype": "markov_fallback"
    }
