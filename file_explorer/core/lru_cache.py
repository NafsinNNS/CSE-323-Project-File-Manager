import os
import time
import threading
from collections import OrderedDict


class LRUMetadataCache:
    def __init__(self, capacity: int = 2048, ttl: float = 2.0):
        self.capacity = capacity
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
        self.enabled = True
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }

    @property
    def size(self):
        with self.lock:
            return len(self._cache)

    @property
    def hit_rate(self):
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return self.stats["hits"] / total * 100

    def reset_stats(self):
        self.stats["hits"] = 0
        self.stats["misses"] = 0
        self.stats["evictions"] = 0

    def _evict(self):
        while len(self._cache) > self.capacity:
            self._cache.popitem(last=False)
            self.stats["evictions"] += 1

    def _is_fresh(self, entry):
        return (time.monotonic() - entry["ts"]) < self.ttl

    def get(self, key: str):
        if not self.enabled:
            return None
        with self.lock:
            entry = self._cache.get(key)
            if entry is not None and self._is_fresh(entry):
                self._cache.move_to_end(key)
                self.stats["hits"] += 1
                return entry["value"]
            if entry is not None:
                del self._cache[key]
            self.stats["misses"] += 1
            return None

    def put(self, key: str, value):
        with self.lock:
            if key in self._cache:
                del self._cache[key]
            self._cache[key] = {"value": value, "ts": time.monotonic()}
            self._evict()

    def invalidate(self, key: str):
        with self.lock:
            self._cache.pop(key, None)

    def invalidate_prefix(self, prefix: str):
        with self.lock:
            to_del = [k for k in self._cache if k.startswith(prefix)]
            for k in to_del:
                del self._cache[k]

    def clear(self):
        with self.lock:
            self._cache.clear()
            self.reset_stats()


_cache = LRUMetadataCache()


def get_cache():
    return _cache


def cached_stat(path: str, monitor=None):
    cache = get_cache()
    key = f"stat:{path}"
    result = cache.get(key)
    if result is not None:
        if monitor:
            monitor._log("cache_hit", f"stat('{path}')", f"cached (age {time.monotonic() - result['ts']:.2f}s)")
        return result["value"]
    value = os.stat(path)
    cache.put(key, {"value": value, "ts": time.monotonic()})
    return value


def cached_listdir(path: str, monitor=None):
    cache = get_cache()
    key = f"listdir:{path}"
    result = cache.get(key)
    if result is not None:
        if monitor:
            monitor._log("cache_hit", f"listdir('{path}')", f"cached ({len(result['value'])} entries)")
        return result["value"]
    entries = os.listdir(path)
    cache.put(key, {"value": entries, "ts": time.monotonic()})
    return entries
