import json
import logging
from datetime import datetime, timezone
from app.extensions import redis_client

logger = logging.getLogger(__name__)

class PresenceService:
    """Manages high-frequency real-time device live state in Redis."""

    REDIS_KEY_PREFIX = "device:"
    REDIS_KEY_SUFFIX = ":presence"
    DEFAULT_TTL_SECONDS = 120

    @classmethod
    def _presence_key(cls, identifier: str) -> str:
        return f"{cls.REDIS_KEY_PREFIX}{identifier}{cls.REDIS_KEY_SUFFIX}"

    @classmethod
    def update_device_presence(
        cls,
        device_id: str,
        status: str = "ONLINE",
        hostname: str = None,
        agent_version: str = "1.0.0",
        ip_address: str = None,
        employee_id: str = None,
        work_state: str = "ACTIVE",
        db_id: str = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS
    ):
        """Update fast in-memory Redis presence record for a device."""
        now_iso = datetime.now(timezone.utc).isoformat()
        state_data = {
            "device_id": device_id,
            "status": status,
            "hostname": hostname or "",
            "agent_version": agent_version,
            "ip_address": ip_address or "",
            "employee_id": employee_id or "",
            "work_state": work_state,
            "last_seen": now_iso
        }
        
        payload_str = json.dumps(state_data)
        
        # Save by device_uuid (primary specification)
        primary_key = cls._presence_key(device_id)
        redis_client.set(primary_key, payload_str, ex=ttl_seconds)

        # Also index by database UUID id if different from device_uuid for fast multi-key resolution
        if db_id and db_id != device_id:
            alias_key = cls._presence_key(db_id)
            redis_client.set(alias_key, payload_str, ex=ttl_seconds)

        return state_data

    @classmethod
    def get_device_presence(cls, identifier: str):
        """Fetch live presence state from Redis by device_uuid or DB id."""
        key = cls._presence_key(identifier)
        raw = redis_client.get(key)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return None

    @classmethod
    def get_all_live_presence(cls):
        """Retrieve live state mapping for all currently active devices."""
        pattern = f"{cls.REDIS_KEY_PREFIX}*{cls.REDIS_KEY_SUFFIX}"
        keys = redis_client.keys(pattern)
        results = {}
        for key in keys:
            raw = redis_client.get(key)
            if raw:
                try:
                    data = json.loads(raw)
                    dev_id = data.get("device_id")
                    if dev_id:
                        results[dev_id] = data
                except Exception:
                    pass
        return results

    @classmethod
    def set_device_status(cls, identifier: str, status: str, db_id: str = None):
        """Update device presence status in Redis."""
        if status == "OFFLINE":
            cls.set_device_offline(identifier, db_id)
        else:
            cls.update_device_presence(device_id=identifier, status=status, db_id=db_id)

    @classmethod
    def set_device_offline(cls, identifier: str, db_id: str = None):
        """Mark device as OFFLINE in Redis."""
        keys = [cls._presence_key(identifier)]
        if db_id and db_id != identifier:
            keys.append(cls._presence_key(db_id))
        redis_client.delete(*keys)

    @classmethod
    def set_device_stale(cls, identifier: str, db_id: str = None):
        """Transition device to STALE status in Redis."""
        current = cls.get_device_presence(identifier)
        if current:
            current["status"] = "STALE"
            payload_str = json.dumps(current)
            redis_client.set(cls._presence_key(identifier), payload_str, ex=60)
            if db_id and db_id != identifier:
                redis_client.set(cls._presence_key(db_id), payload_str, ex=60)
