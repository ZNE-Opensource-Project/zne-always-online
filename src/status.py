import json
import os
import discord
from discord.gateway import DiscordWebSocket, Status


VALID_STATUSES = ["online", "dnd", "idle", "invisible", "mobile"]


class StatusManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self.config = self._load_config()
        self.status_icon = self.config.get("status_icon", "online")
        self.status_msg = self.config.get("status_msg", "Running ZNE Always online 1.0!")
        self._original_identify = None
        self._mobile_patched = False
        if self.status_icon == "mobile":
            self._patch_mobile_identify()

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _parse_status(self, status_str):
        status_str = (status_str or "online").lower()
        mapping = {
            "online": discord.Status.online,
            "dnd": discord.Status.dnd,
            "idle": discord.Status.idle,
            "invisible": discord.Status.invisible,
            "mobile": discord.Status.online,
        }
        return mapping.get(status_str, discord.Status.online)

    def _patch_mobile_identify(self):
        if self._mobile_patched:
            return

        async def mobile_identify(ws):
            presence = {
                "status": "unknown",
                "since": ws.idle_since,
                "activities": [],
                "afk": ws.afk,
            }
            existing = ws._connection.current_session
            if existing is not None:
                presence["status"] = str(existing.status) if existing.status is not Status.offline else "invisible"
                presence["activities"] = [a.to_dict() for a in existing.activities]

            properties = {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            }

            payload = {
                "op": ws.IDENTIFY,
                "d": {
                    "token": ws.token,
                    "capabilities": ws.capabilities.value,
                    "properties": properties,
                    "presence": presence,
                    "compress": not ws._transport_compression,
                    "client_state": {
                        "guild_versions": {},
                    },
                },
            }

            await ws.call_hooks("before_identify", initial=ws._initial_identify)
            await ws.send_as_json(payload)
            ws._initial_identify = True

        self._original_identify = DiscordWebSocket.identify
        DiscordWebSocket.identify = mobile_identify
        self._mobile_patched = True

    async def apply_status(self, client):
        status = self._parse_status(self.status_icon)
        activity = discord.CustomActivity(name=self.status_msg)
        await client.change_presence(status=status, activity=activity)
