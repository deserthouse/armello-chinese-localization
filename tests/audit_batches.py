"""亲审批次管理：打印下一批 + 落盘上一批判决。用法：
python tests/audit_batches.py next [N]         # 打印第 N 批（默认下一批）
python tests/audit_batches.py done <json数组>  # 追加判决到 audit_agent_findings.jsonl
"""
import json
import sys
import os

recs = {json.loads(l)["id"]: json.loads(l) for l in open("master.jsonl", encoding="utf-8")}
sample_ids = json.load(open("tests/audit_sample_ids.json"))
done_ids = set()
if os.path.exists("tests/audit_agent_ids.json"):
    done_ids.update(json.load(open("tests/audit_agent_ids.json")))
if os.path.exists("tests/audit_agent_findings.jsonl"):
    for l in open("tests/audit_agent_findings.jsonl", encoding="utf-8"):
        done_ids.add(json.loads(l)["id"])

PRIO = {"quests": 0, "encounters": 1, "cards": 2, "story": 3, "ui": 4, "items_ach": 5, "misc": 6}

def strata(rid):
    if rid.startswith(("MAINMENU_", "UI_", "CHATMESSAGE_", "CHAT_", "NOTIFICATION_", "MULTIPLAYER_", "SETTINGS")):
        return "ui"
    if rid.startswith("CARD_"):
        return "cards"
    if rid.startswith("QUEST_"):
        return "quests"
    if rid.startswith("ENCOUNTER_"):
        return "encounters"
    if rid.startswith(("GMCC_", "ACCOLADE_", "ACH_")):
        return "items_ach"
    if rid.startswith(("PROLOGUE_", "UI_CLANGROUNDS")):
        return "story"
    return "misc"

remaining = [i for i in sample_ids if i not in done_ids]
remaining.sort(key=lambda i: (PRIO[strata(i)], i))
B = 60
batches = [remaining[k:k + B] for k in range(0, len(remaining), B)]

cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
if cmd == "next":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    batch = batches[n]
    print(f"### 批次 {n+1}/{len(batches)} 本批 {len(batch)} 剩余 {len(remaining)}")
    for j, rid in enumerate(batch):
        r = recs[rid]
        en = (r.get("en") or "").replace("\n", "⏎")[:130]
        zh = (r.get("zh") or "").replace("\n", "⏎")[:85]
        print(f"{j+1}|{rid}|{en}|{zh}")
elif cmd == "done":
    flags = json.loads(sys.argv[2])
    with open("tests/audit_agent_findings.jsonl", "a", encoding="utf-8") as f:
        for fl in flags:
            f.write(json.dumps(fl, ensure_ascii=False) + "\n")
    print(f"落盘 {len(flags)} 条判决")
