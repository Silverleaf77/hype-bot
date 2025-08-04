import os, asyncio, time
from telethon import TelegramClient, events
import redis

# ── Telegram credentials ───────────────────────────────
API_ID   = int(os.getenv("TG_API_ID", "123456"))          # ← replace in Render env
API_HASH = os.getenv("TG_API_HASH", "YOUR_API_HASH")      # ← replace in Render env
SESSION  = "hype-bot"                                    # session file name

# List the groups or channel links/usernames you want to follow
TARGET_CHATS = [
    "https://t.me/INSERT_YOUR_GROUP",    # change these
]

# ── Redis connection ───────────────────────────────────
R = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHATS))
async def handler(event):
    text = event.raw_text.lower()
    for word in text.split():
        if word.startswith("$") and 2 < len(word) < 15:
            coin = word.strip("$").upper()
            now  = int(time.time())
            R.zadd("mentions", {coin: now})     # timestamp of latest mention
            R.zincrby("volume", 1, coin)        # increment mention counter
            print("Hit:", coin)

async def main():
    await client.start()
    print("Telegram collector running…")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
