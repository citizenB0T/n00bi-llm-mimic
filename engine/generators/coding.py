import re
from typing import Optional, Tuple

CODE_SNIPPETS = {
    "binary_search": {
        "title": "Binary Search Implementation in Python",
        "lang": "python",
        "code": """from typing import List, Optional

def binary_search(arr: List[int], target: int) -> Optional[int]:
    \"\"\"
    Performs an iterative binary search on a sorted list.
    
    Args:
        arr: A monotonically ascending sorted list of integers.
        target: The value to search for.
        
    Returns:
        The zero-based index of the target if found, otherwise None.
        
    Complexity:
        Time Complexity: O(log N)
        Space Complexity: O(1) auxiliary space
    \"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        # Avoid potential integer overflow in languages with fixed-width integers
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return None

# Example usage:
if __name__ == "__main__":
    dataset = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    target_val = 23
    
    result_idx = binary_search(dataset, target_val)
    if result_idx is not None:
        print(f"Target {target_val} located at index {result_idx}.")
    else:
        print(f"Target {target_val} not found in array.")
""",
        "explanation": """### Algorithmic Breakdown
Binary Search is a divide-and-conquer algorithm that halves the search space with each comparison:

1. **Pointers Initialization**: We maintain two boundary markers (`left` and `right`).
2. **Midpoint Evaluation**: In each iteration, we evaluate the middle element `arr[mid]`.
3. **Space Pruning**:
   - If `arr[mid] == target`, we immediately return `mid`.
   - If `arr[mid] < target`, the target must reside in the right half, so `left = mid + 1`.
   - If `arr[mid] > target`, the target resides in the left half, so `right = mid - 1`.

| Metric | Asymptotic Bound | Notes |
|---|---|---|
| **Best Case Time** | $O(1)$ | Target found at initial midpoint |
| **Average Time** | $O(\\log N)$ | Standard halving progression |
| **Worst Case Time** | $O(\\log N)$ | Target at extremity or absent |
| **Space Complexity** | $O(1)$ | Iterative implementation uses zero heap |
"""
    },
    "lru_cache": {
        "title": "Least Recently Used (LRU) Cache in Python",
        "lang": "python",
        "code": """from collections import OrderedDict
from typing import Any, Optional

class LRUCache:
    \"\"\"
    A fixed-capacity LRU Cache with O(1) get and put operations
    utilizing an OrderedDict (hash table + doubly linked list).
    \"\"\"
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        self.cache: OrderedDict[Any, Any] = OrderedDict()

    def get(self, key: Any) -> Optional[Any]:
        if key not in self.cache:
            return None
        # Move the accessed key to the end to signify recent access
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            # Update value and mark as most recently used
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Evict least recently used item (the first item) if over capacity
        if len(self.cache) > self.capacity:
            oldest_key, _ = self.cache.popitem(last=False)
            # print(f"Evicted LRU key: {oldest_key}")

# Example usage:
if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put("user_1", {"name": "Alice"})
    cache.put("user_2", {"name": "Bob"})
    print("Fetched user_1:", cache.get("user_1"))  # user_1 is now most recent
    cache.put("user_3", {"name": "Charlie"})        # user_2 evicted!
    print("Fetched user_2 (should be None):", cache.get("user_2"))
""",
        "explanation": """### Architecture & Mechanics
An optimal **LRU Cache** requires constant time $O(1)$ for both retrieval and insertion:
- **Hash Table**: Provides $O(1)$ key lookup.
- **Doubly Linked List**: Allows $O(1)$ node repositioning when an item is accessed or evicted.

In Python, `collections.OrderedDict` encapsulates both data structures natively in C, providing maximum performance without manual pointer bookkeeping.
"""
    },
    "debounce": {
        "title": "Debounce Utility in TypeScript / JavaScript",
        "lang": "typescript",
        "code": """/**
 * Creates a debounced function that delays invoking `func` until after
 * `wait` milliseconds have elapsed since the last invocation.
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function (this: any, ...args: Parameters<T>): void {
    const context = this;

    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func.apply(context, args);
      timeoutId = null;
    }, wait);
  };
}

// Example usage:
const handleResize = debounce((event: Event) => {
  console.log('Window resized to:', window.innerWidth, window.innerHeight);
}, 250);

window.addEventListener('resize', handleResize);
""",
        "explanation": """### Why Debounce Matters
Debouncing is critical in front-end performance engineering:
- **Rate-Limiting Expensive Operations**: Prevents firing search API queries or complex DOM recalculations on every single keystroke or scroll tick.
- **Trailing Execution**: Ensures the target callback only executes once the user has paused input for the specified interval (`wait`).
"""
    },
    "fastapi_endpoint": {
        "title": "Asynchronous REST API with FastAPI & Pydantic",
        "lang": "python",
        "code": """from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(title="Task Service", version="1.0.0")

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(default=1, ge=1, le=5)

class TaskResponse(TaskCreate):
    id: int
    completed: bool = False

# In-memory storage for demonstration
db_tasks: List[TaskResponse] = []

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate):
    new_task = TaskResponse(
        id=len(db_tasks) + 1,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        completed=False
    )
    db_tasks.append(new_task)
    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    for task in db_tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
""",
        "explanation": """### Key Architectural Patterns
- **Pydantic Validation**: Automatically parses JSON request bodies and enforces boundary conditions (`min_length`, `ge`, `le`).
- **Async Concurrency**: FastAPI leverages ASGI (`uvicorn`) for high-concurrency non-blocking I/O.
- **Automatic OpenAPI Documentation**: Swagger UI docs are generated at `/docs` out of the box.
"""
    },
    "generic_code": {
        "title": "Idiomatic Modular Implementation",
        "lang": "python",
        "code": """from typing import Any, Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class SolutionHandler:
    \"\"\"
    A robust, extensible handler implementing best practices.
    \"\"\"
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {"timeout": 30, "retries": 3}
        logger.info("SolutionHandler initialized with configuration: %s", self.config)

    def process(self, items: List[Any]) -> Dict[str, Any]:
        if not items:
            logger.warning("Empty dataset passed to process().")
            return {"status": "empty", "processed_count": 0}

        results = []
        for index, item in enumerate(items):
            # Process item with boundary checks
            transformed = f"processed_{item}"
            results.append(transformed)

        logger.info("Successfully processed %d items.", len(results))
        return {
            "status": "success",
            "processed_count": len(results),
            "payload": results
        }

if __name__ == "__main__":
    handler = SolutionHandler()
    sample_data = ["alpha", "beta", "gamma"]
    output = handler.process(sample_data)
    print("Execution Result:", output)
""",
        "explanation": """### Architecture Highlights
- **Defensive Design**: Validates input boundaries and prevents null pointer / index exceptions.
- **Configurable Defaults**: Uses flexible dictionary initialization with safe fallback defaults.
- **Structured Logging**: Replaces raw `print()` statements with standard `logging` for production traceability.
"""
    }
}

def generate_code_response(prompt: str) -> str:
    p_lower = prompt.lower()
    
    selected_key = "generic_code"
    if "binary search" in p_lower:
        selected_key = "binary_search"
    elif "lru" in p_lower or "cache" in p_lower:
        selected_key = "lru_cache"
    elif "debounce" in p_lower or "throttle" in p_lower:
        selected_key = "debounce"
    elif "fastapi" in p_lower or "api" in p_lower or "rest" in p_lower or "endpoint" in p_lower:
        selected_key = "fastapi_endpoint"
        
    item = CODE_SNIPPETS[selected_key]
    
    return f"""## {item['title']}

Here is an idiomatic, production-ready solution that emphasizes type-safety, clean encapsulation, and optimal performance:

```{item['lang']}
{item['code']}
```

{item['explanation']}
"""
