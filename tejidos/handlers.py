from typing import Any, Dict
from tejidos.util import my_sum

def sum_handler(event: Any, _context: Any) -> Dict:

    return {"sum": my_sum(first=event.get("first"), second=event.get("second"))}
