import asyncio
import redis.asyncio as redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

async def consume():
    last_id = "$"
    while True:
        messages = await r.xread({"events": last_id}, block=1000, count=1)
        for stream, entries in messages:
            for id, data in entries:
                print(f"[{data['timestamp']}] {data['event_type']} by {data['user_id']}: {data['amount']}")
                last_id = id

if __name__ == "__main__":
    asyncio.run(consume())
