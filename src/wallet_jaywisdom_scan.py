#!/usr/bin/env python3
import os, json, requests
from datetime import datetime, UTC

RPC=os.getenv("BASE_RPC_URL","https://mainnet.base.org")
WALLET=os.getenv("TARGET_WALLET","0x829adfedbe565f9885a7ea6bc78912acaef055e2").lower()
TOKEN=os.getenv("JAYWISDOM_TOKEN","0x84dc68b4354be610c44fe63dcadbf56847f7476b").lower()
START=int(os.getenv("START_BLOCK","28500000"))
END=int(os.getenv("END_BLOCK","28520000"))
LIMIT=int(os.getenv("LIMIT","1000"))

def rpc(method, params):
    r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=30)
    r.raise_for_status()
    return r.json()["result"]

entries=[]
for b in range(START, END+1):
    block=rpc("eth_getBlockByNumber",[hex(b), True])
    if not block: continue
    for tx in block.get("transactions",[]):
        if len(entries)>=LIMIT: break
        frm=(tx.get("from") or "").lower()
        to=(tx.get("to") or "").lower()
        if frm==WALLET or to==WALLET or to==TOKEN:
            receipt=rpc("eth_getTransactionReceipt",[tx["hash"]])
            touches_token = to==TOKEN or any((log.get("address","").lower()==TOKEN) for log in receipt.get("logs",[]))
            if touches_token or frm==WALLET or to==WALLET:
                entries.append({
                    "block": int(tx["blockNumber"],16),
                    "tx_hash": tx["hash"],
                    "from": frm,
                    "to": to,
                    "touches_jaywisdom_token": touches_token,
                    "log_count": len(receipt.get("logs",[]))
                })
    if len(entries)>=LIMIT: break
    if b % 100 == 0: print("block", b, "entries", len(entries))

out={
  "status":"WALLET_SCAN_COMPLETED",
  "wallet":WALLET,
  "jaywisdom_token":TOKEN,
  "scan_range":{"from":START,"to":END},
  "entries_count":len(entries),
  "limit":LIMIT,
  "timestamp":datetime.now(UTC).isoformat(),
  "entries":entries
}
os.makedirs("evidence",exist_ok=True)
open("evidence/EV-BBC-003A-WALLET-JAYWISDOM-SCAN.json","w").write(json.dumps(out,indent=2))
print(json.dumps({k:out[k] for k in out if k!="entries"},indent=2))
