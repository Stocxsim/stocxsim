import threading
import time
from typing import Any, Dict, Optional

# Simple in-memory cache for computed indicators.
# This avoids fetching candles on every stock page open.

_TTL_SECONDS = 300  # 5 minutes
_cache_lock = threading.Lock()
_cache: Dict[str, Dict[str, Any]] = {}
_inflight: set[str] = set()


def get_cached_indicators(token: str) -> Optional[Dict[str, Any]]:
    token = str(token)
    now = time.time()
    with _cache_lock:
        item = _cache.get(token)
        if not item:
            return None
        if now - float(item.get("ts", 0)) > _TTL_SECONDS:
            _cache.pop(token, None)
            return None
        return dict(item.get("data") or {})


def mark_inflight(token: str) -> bool:
    token = str(token)
    with _cache_lock:
        if token in _inflight:
            return False
        _inflight.add(token)
        return True


def unmark_inflight(token: str) -> None:
    token = str(token)
    with _cache_lock:
        _inflight.discard(token)


def set_cached_indicators(token: str, data: Dict[str, Any]) -> None:
    token = str(token)
    with _cache_lock:
        _cache[token] = {"ts": time.time(), "data": data}


def compute_and_cache_indicators(token: str) -> None:
    """Compute RSI/EMA values and cache them.

    Runs best in a background thread.
    """
    token = str(token)
    if not mark_inflight(token):
        return

    try:
        from service.stockservice import rsi_cal, ema_cal, get_closes

        closes = get_closes(token)
        rsi = rsi_cal(closes)
        ema9 = ema_cal(closes, 9)
        ema20 = ema_cal(closes, 20)

        set_cached_indicators(token, {"rsi": rsi, "ema_9": ema9, "ema_20": ema20})
    except Exception:
        # Never fail request path due to indicator calculation.
        # If computation fails, keep cache empty and allow retry later.
        return
    finally:
        unmark_inflight(token)
