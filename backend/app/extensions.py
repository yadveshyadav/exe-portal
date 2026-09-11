import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
# async_mode='threading' is universally compatible across Windows/Linux/macOS with standard WSGI & simple-websocket
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

# Redis connection management with graceful fallback
class RedisWrapper:
    def __init__(self):
        self._client = None
        self._mock_storage = {}

    def init_app(self, app):
        redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
        if redis_url and redis_url != "redis://mock":
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
                # Quick ping to verify connectivity
                self._client.ping()
            except Exception as e:
                app.logger.warning(f"Redis connection failed ({e}). Falling back to internal in-memory store for dev/testing.")
                self._client = None
        else:
            self._client = None

    def get(self, key):
        if self._client:
            try:
                return self._client.get(key)
            except Exception:
                pass
        return self._mock_storage.get(key)

    def set(self, key, value, ex=None):
        if self._client:
            try:
                return self._client.set(key, value, ex=ex)
            except Exception:
                pass
        self._mock_storage[key] = str(value)
        return True

    def delete(self, *keys):
        if self._client:
            try:
                return self._client.delete(*keys)
            except Exception:
                pass
        for k in keys:
            self._mock_storage.pop(k, None)
        return True

    def hset(self, name, key=None, value=None, mapping=None):
        if self._client:
            try:
                return self._client.hset(name, key=key, value=value, mapping=mapping)
            except Exception:
                pass
        if name not in self._mock_storage or not isinstance(self._mock_storage[name], dict):
            self._mock_storage[name] = {}
        if mapping:
            self._mock_storage[name].update({k: str(v) for k, v in mapping.items()})
        elif key:
            self._mock_storage[name][key] = str(value)
        return True

    def hget(self, name, key):
        if self._client:
            try:
                return self._client.hget(name, key)
            except Exception:
                pass
        h = self._mock_storage.get(name)
        if isinstance(h, dict):
            return h.get(key)
        return None

    def hgetall(self, name):
        if self._client:
            try:
                return self._client.hgetall(name)
            except Exception:
                pass
        h = self._mock_storage.get(name)
        return h if isinstance(h, dict) else {}

    def keys(self, pattern="*"):
        if self._client:
            try:
                return self._client.keys(pattern)
            except Exception:
                pass
        import fnmatch
        return [k for k in self._mock_storage.keys() if fnmatch.fnmatch(k, pattern)]

    def publish(self, channel, message):
        if self._client:
            try:
                return self._client.publish(channel, message)
            except Exception:
                pass
        return 1

redis_client = RedisWrapper()
