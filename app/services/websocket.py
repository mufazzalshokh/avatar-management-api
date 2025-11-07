from fastapi import WebSocket
from typing import Dict, Set
from datetime import datetime


class ConnectionManager:
    """
    WebSocket connection manager for handling multiple client connections
    and broadcasting avatar change notifications
    """

    def __init__(self):
        # Map of user_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection
            user_id: User ID associated with this connection
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove a WebSocket connection

        Args:
            websocket: WebSocket connection to remove
            user_id: User ID associated with this connection
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    def disconnect_all_user_connections(self, user_id: int):
        """
        Disconnect all WebSocket connections for a specific user

        Args:
            user_id: User ID whose connections should be closed
        """
        if user_id in self.active_connections:
            connections = self.active_connections[user_id].copy()
            for websocket in connections:
                # Close connection without waiting
                try:
                    websocket.close()
                except:
                    pass
            del self.active_connections[user_id]

    async def send_avatar_update(self, user_id: int, avatar_url: str):
        """
        Send avatar update notification to all connections of a user

        Args:
            user_id: User ID whose avatar was updated
            avatar_url: New avatar URL
        """
        if user_id not in self.active_connections:
            return

        message = {
            "type": "avatar_updated",
            "user_id": user_id,
            "avatar_url": avatar_url,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send to all connections for this user
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                # Mark for removal if send fails
                disconnected.append(websocket)

        # Clean up failed connections
        for websocket in disconnected:
            self.disconnect(websocket, user_id)


# Global connection manager instance
manager = ConnectionManager()