import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Tracks active connected WebSocket sockets and their session associations."""

    def __init__(self):
        self.connected_agents = {}  # sid -> {device_uid, company_id, device_id}
        self.connected_portal_users = {}  # sid -> {user_id, company_id}

    def register_agent(self, sid: str, device_uid: str, company_id: str, device_id: str):
        self.connected_agents[sid] = {
            "device_uid": device_uid,
            "company_id": company_id,
            "device_id": device_id
        }
        logger.info(f"Agent registered on WS SID {sid} for Device UID {device_uid}")

    def register_portal_user(self, sid: str, user_id: str, company_id: str):
        self.connected_portal_users[sid] = {
            "user_id": user_id,
            "company_id": company_id
        }
        logger.info(f"Portal user {user_id} connected on WS SID {sid}")

    def remove_connection(self, sid: str):
        if sid in self.connected_agents:
            agent = self.connected_agents.pop(sid)
            logger.info(f"Agent disconnected WS SID {sid} ({agent.get('device_uid')})")
            return "agent", agent
        elif sid in self.connected_portal_users:
            user = self.connected_portal_users.pop(sid)
            logger.info(f"Portal user disconnected WS SID {sid} ({user.get('user_id')})")
            return "user", user
        return None, None

    def get_agent_sids(self, device_identifier: str):
        """Find all active socket IDs associated with a device UUID or DB ID."""
        sids = []
        for sid, info in self.connected_agents.items():
            if info.get("device_uid") == device_identifier or info.get("device_id") == device_identifier:
                sids.append(sid)
        return sids

    def is_agent_connected(self, device_identifier: str) -> bool:
        return len(self.get_agent_sids(device_identifier)) > 0

    def get_company_portal_sids(self, company_id: str):
        return [sid for sid, info in self.connected_portal_users.items() if info.get("company_id") == company_id]

connection_manager = ConnectionManager()
