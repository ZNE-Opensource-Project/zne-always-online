import json
import os
import discord


VALID_STATUSES = ["online", "dnd", "idle", "invisible", "mobile"]


class StatusManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self.config = self._load_config()
        self.status_icon = self.config.get("status_icon", "online")
        self.status_msg = self.config.get("status_msg", "Running ZNE Always online 1.0!")

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

    async def apply_status(self, client):
        status = self._parse_status(self.status_icon)
        activity = discord.CustomActivity(name=self.status_msg)
        await client.change_presence(status=status, activity=activity)
