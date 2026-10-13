"""In-memory sliding-window rate limiter.

State lives in the process: with several workers each one counts on its own,
so the effective limit is `limit * workers`. Good enough for a single instance;
use a shared store (e.g. Redis) behind a load balancer.
"""

import math
import threading
import time
from collections import deque
from collections.abc import Callable

_UNITS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}


def parse_rate(rate: str) -> tuple[int, int]:
    """Parse "10/minute" into (10, 60). Accepts second, minute, hour and day."""
    count, _, unit = rate.partition("/")
    try:
        limit = int(count)
        window = _UNITS[unit.strip().lower()]
    except (ValueError, KeyError):
        raise ValueError(
            f'Invalid rate "{rate}": expected "<count>/<second|minute|hour|day>", '
            'e.g. "10/minute"'
        ) from None
    if limit < 1:
        raise ValueError(f'Invalid rate "{rate}": count must be at least 1')
    return limit, window


class SlidingWindowLimiter:
    # keys are swept once the table grows beyond this size
    _SWEEP_THRESHOLD = 10_000

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._windows: dict[str, int] = {}
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window: int) -> int | None:
        """Register a request. Returns None if allowed, otherwise the number of
        seconds to wait before the next request is accepted."""
        now = self._clock()
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            self._windows[key] = window
            while hits and hits[0] <= now - window:
                hits.popleft()
            if len(hits) >= limit:
                return max(1, math.ceil(hits[0] + window - now))
            hits.append(now)
            if len(self._hits) > self._SWEEP_THRESHOLD:
                self._sweep(now)
            return None

    def _sweep(self, now: float) -> None:
        for key in [
            k
            for k, hits in self._hits.items()
            if not hits or hits[-1] <= now - self._windows[k]
        ]:
            del self._hits[key]
            del self._windows[key]

    def clear(self) -> None:
        with self._lock:
            self._hits.clear()
            self._windows.clear()
