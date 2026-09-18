"""审计聚合：换行类复查（文件版，无shell转义坑）+ 全部判决统计。"""
import json
import re
from collections import Counter, defaultdict

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
LIT_N = "\\" + "n"  # 字面反斜杠+n

lit_keep = lit_real = []
lit_keep = 0
lit_real = 0
for r in recs:
    en, zh = r.get("en", ""), r.get("zh", "")
    if LIT_N in en:
        if LIT_N in zh:
            lit_keep += 1
        elif "\n" in zh:
            lit_real += 1
print(f"EN含字面\\n 共 {lit_keep + lit_real} 条: zh保留字面={lit_keep} / zh转真实换行={lit_real}")

# 官中基准
off_keep = off_real = 0
for r in recs:
    en, off = r.get("en", ""), r.get("zh_official") or ""
    if LIT_N in en and off:
        if LIT_N in off:
            off_keep += 1
        elif "\n" in off:
            off_real += 1
print(f"官中基准: 保留字面={off_keep} / 真实换行={off_real}")

# 亲审判决统计
flags = [json.loads(l) for l in open("tests/audit_agent_findings.jsonl", encoding="utf-8")]
seen = {}
for f in flags:
    seen[f["id"]] = f
cls_count = Counter(f["cls"] for f in seen.values())

# 分层统计
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

sample_ids = json.load(open("tests/audit_sample_ids.json"))
reviewed = set(seen) | set(json.load(open("tests/audit_agent_ids.json")))
strat_total = Counter(strata(i) for i in sample_ids)
strat_flag = Counter(strata(f["id"]) for f in seen.values() if strata(f["id"]) in strat_total)

print(f"\n亲审覆盖: {len(reviewed & set(sample_ids))}/{len(sample_ids)} 样本")
print(f"标记条目: {len(seen)} ({len(seen)/len(reviewed & set(sample_ids))*100:.0f}% of reviewed)")
print("\n按类别:")
for c, n in cls_count.most_common():
    print(f"  {c}: {n}")
print("\n按层错误率(标记/样本):")
for s in ("quests", "encounters", "cards", "story", "ui", "items_ach", "misc"):
    if strat_total[s]:
        print(f"  {s}: {strat_flag.get(s, 0)}/{strat_total[s]} = {strat_flag.get(s, 0)/strat_total[s]*100:.0f}%")

json.dump(list(seen.values()), open("tests/audit_agent_findings_dedup.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n去重判决已存 tests/audit_agent_findings_dedup.json")
