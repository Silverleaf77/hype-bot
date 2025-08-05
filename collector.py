import os, asyncio, time
import redis
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- credentials from Render env ---
API_ID   = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION  = os.environ["STRING_SESSION"]

# --- groups/channels to watch (YOU must be a member) ---
TARGET_CHATS = [
    "https://t.me/BossmanCallsOfficial",   # <-- put a real group link or @username
]

# --- Redis connection ---
R = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

# Use StringSession so Render never prompts for phone/code
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHATS))
async def handler(event):
    text = (event.raw_text or "").lower()
    for word in text.split():
        if word.startswith("$") and 2 < len(word) < 15:
            coin = word.strip("$").upper()
            now  = int(time.time())
            R.zadd("mentions", {coin: now})   # latest mention timestamp
            R.zincrby("volume", 1, coin)      # mention counter
            print("Hit:", coin)

async def main():
    await client.start()
    print("Telegram collector running…")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
