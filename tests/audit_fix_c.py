"""C类清扫：新采纳规则的存量修复（EN 作用域 + 断言）。"""
import json
import re

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]

RULES = [
    (r"Palace", [("从宫殿", "从王宫"), ("宫殿", "王宫")]),
    (r"Stone Circle", [("巨石阵", "石环")]),
    (r"Explode Pool", [("爆炸池", "爆发池")]),
    (r"\bGold\b", [("黄金", "金币")]),
    (r"Bounty", [("赏金骰子", "悬赏骰子")]),
    (r"[Bb]onus [Dd]ie", [("赏金骰子", "加成骰子")]),
    (r"Pierce|Piercing", [("刺穿", "贯穿")]),
    (r"Squire", [("（护卫）", "（侍从）")]),
]
WORD_FIX = [("统制", "统治")]

def scope_match(pat, en):
    return re.search(r"(?<![A-Za-z])" + pat + r"(?![A-Za-z])", en, re.IGNORECASE)

stats = {}
changed = 0
for r in recs:
    en, zh = r.get("en", ""), r.get("zh", "")
    if not zh:
        continue
    nz = zh
    for pat, mapping in RULES:
        if scope_match(pat, en):
            for old, new in mapping:
                if old in nz:
                    nz = nz.replace(old, new)
                    stats[f"{old}→{new}"] = stats.get(f"{old}→{new}", 0) + 1
    for old, new in WORD_FIX:
        if old in nz:
            nz = nz.replace(old, new)
            stats[f"{old}→{new}"] = stats.get(f"{old}→{new}", 0) + 1
    # 风味文统一加引号：CARD_*FLAVORTEXT 且非署名行，缺首引号则补
    if re.match(r"CARD_\w+_FLAVORTEXT$", r["id"]) and nz and not nz.startswith("“"):
        core = nz.strip()
        if core.endswith("”"):
            core = core[:-1]
        nz2 = "“" + core + "”"
        if nz2 != nz:
            nz = nz2
            stats["风味文加引号"] = stats.get("风味文加引号", 0) + 1
    if nz != zh:
        r["zh"] = nz
        r.setdefault("provenance", []).append({"r": "auditC", "by": "auto", "v": "规则蒸馏存量清扫"})
        changed += 1

out = [json.dumps(r, ensure_ascii=False) + "\n" for r in recs]
open("master.jsonl", "w", encoding="utf-8").writelines(out)
print(f"C类清扫 {changed} 条")
for k, v in sorted(stats.items(), key=lambda kv: -kv[1]):
    print(f"  {k}: {v}")
