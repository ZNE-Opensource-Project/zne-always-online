import asyncio
import json
import os
import discord
from .status import StatusManager


TOKEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    config_path = os.path.join(TOKEN_DIR, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_tokens():
    config = load_config()
    tokens = config.get("tokens")
    if isinstance(tokens, list):
        return [t for t in tokens if isinstance(t, str) and t.strip()]
    token = config.get("token")
    if isinstance(token, str) and token.strip():
        return [token.strip()]
    return []


class ZNESelfBot:
    def __init__(self, token, status_manager):
        self.token = token
        self.status_manager = status_manager
        intents = discord.Intents.default()
        intents.message_content = False
        self.client = discord.Client(self_bot=True, intents=intents)

        @self.client.event
        async def on_ready():
            print(f"Logged in as {self.client.user}")
            await self.status_manager.apply_status(self.client)

    async def start(self):
        await self.client.start(self.token)


async def run_all():
    tokens = get_tokens()
    if not tokens:
        print("No tokens found in config.json")
        return

    status_manager = StatusManager()
    bots = [ZNESelfBot(token, status_manager) for token in tokens]
    await asyncio.gather(*[bot.start() for bot in bots])


def main():
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
