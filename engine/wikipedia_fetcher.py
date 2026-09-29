import json
import re
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any

USER_AGENT = "n00bi-bot/1.0 (Educational deterministic LLM mimic; contact: admin@noobi.local)"
TIMEOUT = 4.0

def clean_wiki_query(raw_query: str) -> str:
    """
    Cleans up leading articles, punctuation, and extra whitespace from query.
    e.g. "la théorie de la relativité ?" -> "théorie de la relativité"
         "un trou noir" -> "trou noir"
    """
    q = raw_query.strip().rstrip("?.! ")
    # Strip leading polite words
    q = re.sub(r"^(?:s'il\s+te\s+pla[îi]t|svp|stp|peux[- ]tu\s+me\s+dire)\s+", "", q, flags=re.IGNORECASE)
    # Strip leading articles
    q = re.sub(r"^(?:le|la|les|l'|un|une|des|du|de\s+la|d')\s*", "", q, flags=re.IGNORECASE)
    return q.strip()

def fetch_wikipedia_summary(query: str) -> Optional[Dict[str, Any]]:
    """
    Fetches French Wikipedia article summary using Wikipedia REST API v1.
    Performs a 2-step lookup:
    1. Direct summary fetch via /api/rest_v1/page/summary/{title}
    2. Fallback search via /w/api.php?action=query&list=search if direct fails
    """
    cleaned = clean_wiki_query(query)
    if not cleaned:
        return None

    # Step 1: Direct summary attempt
    encoded_title = urllib.parse.quote(cleaned.replace(" ", "_"), safe="")
    summary_url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(summary_url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                extract = data.get("extract")
                title = data.get("title")
                if extract and data.get("type") != "disambiguation":
                    return {
                        "title": title or cleaned,
                        "extract": extract,
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    }
    except Exception:
        pass

    # Step 2: Fallback search if direct attempt failed
    search_params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": cleaned,
        "format": "json",
        "srlimit": "1",
        "utf8": "1"
    })
    search_url = f"https://fr.wikipedia.org/w/api.php?{search_params}"

    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                search_data = json.loads(resp.read().decode("utf-8"))
                search_results = search_data.get("query", {}).get("search", [])
                if search_results:
                    best_title = search_results[0].get("title")
                    if best_title:
                        # Fetch summary for the best matched title
                        encoded_best = urllib.parse.quote(best_title.replace(" ", "_"), safe="")
                        best_summary_url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{encoded_best}"
                        req_best = urllib.request.Request(best_summary_url, headers=headers)
                        with urllib.request.urlopen(req_best, timeout=TIMEOUT) as resp_best:
                            if resp_best.status == 200:
                                data_best = json.loads(resp_best.read().decode("utf-8"))
                                extract = data_best.get("extract")
                                if extract:
                                    return {
                                        "title": data_best.get("title", best_title),
                                        "extract": extract,
                                        "url": data_best.get("content_urls", {}).get("desktop", {}).get("page", "")
                                    }
    except Exception:
        pass

    return None
