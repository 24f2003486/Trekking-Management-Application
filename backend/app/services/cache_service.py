"""Reusable Redis caching service for Trekking Management Application V2."""
import fnmatch
import json
import logging
import time
from typing import Any, Optional
import redis
from flask import Flask, current_app

logger = logging.getLogger(__name__)


class CacheService:
    """Enterprise-grade Redis caching layer with graceful degradation and pattern invalidation."""

    def __init__(self, app: Optional[Flask] = None):
        self._redis: Optional[redis.Redis] = None
        self._prefix: str = "tma"
        self._default_ttl: int = 300
        self._memory_store: dict[str, tuple[str, float]] = {}
        self._force_memory: bool = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize Redis connection and caching settings from Flask app config."""
        redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
        self._prefix = app.config.get("CACHE_KEY_PREFIX", "tma")
        self._default_ttl = int(app.config.get("CACHE_DEFAULT_TIMEOUT", 300))
        self._force_memory = app.config.get("CACHE_TYPE") == "memory"

        if not self._force_memory:
            try:
                self._redis = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=2.0,
                    socket_connect_timeout=2.0,
                )
                logger.info("CacheService initialized with Redis at %s (prefix: %s)", redis_url, self._prefix)
            except Exception as exc:
                logger.warning("CacheService failed to connect to Redis at %s: %s. Caching will degrade gracefully.", redis_url, exc)
                self._redis = None
        else:
            self._redis = None
            logger.info("CacheService running in memory-only test mode.")

        app.extensions["cache_service"] = self

    @property
    def client(self) -> Optional[redis.Redis]:
        """Return the active Redis client or None if unavailable / in memory mode."""
        if self._force_memory:
            return None
        if self._redis is None:
            try:
                redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0") if current_app else "redis://localhost:6379/0"
                self._redis = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=2.0,
                    socket_connect_timeout=2.0,
                )
            except Exception:
                return None
        return self._redis

    def is_available(self) -> bool:
        """Check if Redis server is currently reachable."""
        try:
            c = self.client
            return c is not None and c.ping()
        except Exception as exc:
            logger.warning("Redis is unavailable: %s", exc)
            return False

    def build_key(self, namespace: str, identifier: str) -> str:
        """Build a namespaced Redis key with application prefix."""
        prefix = current_app.config.get("CACHE_KEY_PREFIX", self._prefix) if current_app else self._prefix
        return f"{prefix}:{namespace}:{identifier}"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize a JSON-cached value from Redis or fallback store.
        
        Returns None on cache MISS, expiration, or Redis failure.
        """
        try:
            c = self.client
            if c is not None:
                val = c.get(key)
                if val is None:
                    logger.debug("Cache MISS for key: %s", key)
                    return None
                data = json.loads(val)
                logger.info("Cache HIT for key: %s", key)
                return data
        except (redis.RedisError, ConnectionError, TimeoutError) as exc:
            logger.warning("Redis error on GET '%s': %s. Bypassing cache.", key, exc)
            return None
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("JSON decode error for cache key '%s': %s. Discarding invalid cache entry.", key, exc)
            self.delete(key)
            return None

        # Fallback in-memory store if memory mode explicitly enabled
        if self._force_memory and key in self._memory_store:
            val_str, expires_at = self._memory_store[key]
            if time.time() > expires_at:
                del self._memory_store[key]
                logger.debug("Memory cache expired for key: %s", key)
                return None
            logger.info("Memory cache HIT for key: %s", key)
            return json.loads(val_str)

        return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Serialize and store a value in Redis with a TTL in seconds.
        
        Returns True on success, False on failure.
        """
        ttl = timeout if timeout is not None else self._default_ttl
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError) as exc:
            logger.error("Serialization error for cache key '%s': %s", key, exc)
            return False

        try:
            c = self.client
            if c is not None:
                success = c.set(key, serialized, ex=ttl)
                logger.debug("Cache SET for key: %s (TTL: %ss, success: %s)", key, ttl, success)
                return bool(success)
        except (redis.RedisError, ConnectionError, TimeoutError) as exc:
            logger.warning("Redis error on SET '%s': %s. Cache write skipped.", key, exc)
            return False

        if self._force_memory:
            self._memory_store[key] = (serialized, time.time() + ttl)
            return True

        return False

    def delete(self, key: str) -> bool:
        """Delete an individual cache key from Redis or fallback store."""
        deleted = False
        try:
            c = self.client
            if c is not None:
                c.delete(key)
                deleted = True
                logger.debug("Cache DELETE key: %s", key)
        except (redis.RedisError, ConnectionError, TimeoutError) as exc:
            logger.warning("Redis error on DELETE '%s': %s", key, exc)

        if key in self._memory_store:
            del self._memory_store[key]
            deleted = True

        return deleted

    def delete_pattern(self, pattern: str) -> int:
        """Safely delete all keys matching pattern using non-blocking scan_iter."""
        deleted_count = 0
        try:
            c = self.client
            if c is not None:
                keys_to_delete = list(c.scan_iter(match=pattern, count=100))
                if keys_to_delete:
                    deleted_count = c.delete(*keys_to_delete)
                    logger.info("Cache INVALIDATE pattern '%s' cleared %d keys in Redis", pattern, deleted_count)
        except (redis.RedisError, ConnectionError, TimeoutError) as exc:
            logger.warning("Redis error on delete_pattern '%s': %s", pattern, exc)

        # Clear matching keys in memory store
        mem_matching = [k for k in self._memory_store if fnmatch.fnmatch(k, pattern)]
        for k in mem_matching:
            del self._memory_store[k]
            deleted_count += 1

        return deleted_count

    def clear_prefix(self, namespace: str) -> int:
        """Clear all keys under a given namespace (e.g. 'treks')."""
        prefix = current_app.config.get("CACHE_KEY_PREFIX", self._prefix) if current_app else self._prefix
        pattern = f"{prefix}:{namespace}:*"
        return self.delete_pattern(pattern)

    def clear_all(self) -> int:
        """Clear all application-scoped cache entries without affecting other Redis DB keys."""
        prefix = current_app.config.get("CACHE_KEY_PREFIX", self._prefix) if current_app else self._prefix
        pattern = f"{prefix}:*"
        return self.delete_pattern(pattern)

    def invalidate_trek_cache(self, trek_id: Optional[int] = None) -> None:
        """Invalidate trek listings and specific trek details upon mutations.
        
        Args:
            trek_id: If specified, invalidates the exact trek detail keys for both
                     trekker and admin views, plus all trek list queries.
        """
        prefix = current_app.config.get("CACHE_KEY_PREFIX", self._prefix) if current_app else self._prefix
        
        # 1. Invalidate all trek listing caches (both Trekker and Admin listings)
        self.delete_pattern(f"{prefix}:treks:trekker:list:*")
        self.delete_pattern(f"{prefix}:treks:admin:list:*")

        # 2. Invalidate specific trek detail cache if trek_id provided
        if trek_id is not None:
            self.delete(f"{prefix}:treks:trekker:detail:{trek_id}")
            self.delete(f"{prefix}:treks:admin:detail:{trek_id}")
            logger.info("Cache INVALIDATE: cleared listings and details for trek #%s", trek_id)
        else:
            # If no trek_id specified, clear all trek detail caches as well
            self.delete_pattern(f"{prefix}:treks:trekker:detail:*")
            self.delete_pattern(f"{prefix}:treks:admin:detail:*")
            logger.info("Cache INVALIDATE: cleared all trek listings and details")


# Global singleton instance
cache_service = CacheService()
