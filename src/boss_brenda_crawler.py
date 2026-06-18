#!/usr/bin/env python3
import os, json, asyncio
from datetime import datetime
from web3 import AsyncWeb3

env = {}
with open(".env") as f:
    for line in f:
        if line.strip() and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(env["BASE_RPC_URL"]))
CHAIN = env.get("CHAIN", "base")
START_BLOCK = int(env.get("START_BLOCK", 25000000))
END_BLOCK = int(env.get("END_BLOCK", START_BLOCK + 20000))
CHUNK = int(env.get("CHUNK_SIZE", 2000))
ZORA_FACTORY = env.get("ZORA_FACTORY", "0x777777751622c0d3258f214F9DF38E35BF45baF3")

async def main():
    latest = await w3.eth.block_number
    current = min(END_BLOCK, latest)
    results = {
        "chain": CHAIN,
        "factory": ZORA_FACTORY,
        "logs_found": 0,
        "scan_range": {"from": START_BLOCK, "to": current},
        "status": "LIVE_FACTORY_LOG_SCAN_COMPLETED",
        "timestamp": datetime.utcnow().isoformat(),
        "provider": env["BASE_RPC_URL"]
    }

    b = START_BLOCK
    while b <= current:
        to_block = min(b + CHUNK, current)
        logs = await w3.eth.get_logs({
            "fromBlock": b,
            "toBlock": to_block,
            "address": ZORA_FACTORY
        })
        results["logs_found"] += len(logs)
        print(f"{b}-{to_block}: {len(logs)} logs")
        b = to_block + 1

    os.makedirs("data/zora", exist_ok=True)
    with open("data/zora/boss-brenda-zora-registry.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
