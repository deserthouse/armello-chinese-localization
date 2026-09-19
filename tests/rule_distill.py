"""规则蒸馏：RULE 候选 vs 现有 GLOSSARY/专名表 → 仅输出新增/冲突项。"""
import json
import re

rules = []
for l in open("tests/threeway_rules_full.txt", encoding="utf-8"):
    m = re.match(r"^\[\d+\]\s*(\S+)\s*\|\s*(.*)$", l.strip())
    if m:
        rules.append((m.group(1), m.group(2)))

names = json.load(open("tests/glossary_names_v12.json", encoding="utf-8"))
gloss_md = open("GLOSSARY.md", encoding="utf-8").read()
style_md = open("STYLE_GUIDE.md", encoding="utf-8").read()
canon = {k.lower(): v["zh"] for k, v in names.items()}

# 去重
seen = {}
for c, t in rules:
    seen.setdefault(t[:20], (c, t))
print(f"输入 {len(rules)} → 去重 {len(seen)}")

new, conflict, known = [], [], []
for c, t in seen.values():
    tl = t.lower()
    # 冲突检测：提到的英文词的现规范译名 vs 规则中给出的不同译名
    m = re.search(r"([A-Za-z][A-Za-z'\- ]{2,30}?)\s*(?:→|=>|统一[译为]?作?|译[为作]|应译)", t)
    hit_known = False
    for en, zh in canon.items():
        if en in tl and zh in t:
            hit_known = True
            break
    if hit_known:
        known.append((c, t))
        continue
    in_assets = any(k in t for k in ("巫蛊娃娃", "游骑兵", "声望", "间谍大师", "鸦喙", "易容面具",
                                      "铸币大师", "镜影披风", "翅靴", "随从", "腐化", "地块"))
    if in_assets:
        known.append((c, t))
    else:
        new.append((c, t))

# 冲突专项：Terrorised / Rangers 等我已知的人工裁决点
for c, t in seen.values():
    if "Terroris" in t or "摧毁" in t:
        conflict.append((c, t))

print(f"已知/重复 {len(known)} | 待仲裁新增 {len(new)} | 冲突 {len(conflict)}")
print("\n== 冲突（需人工裁决）==")
for c, t in conflict[:10]:
    print(f"  [{c}] {t[:110]}")
print("\n== 新增候选（去重后）==")
for c, t in new:
    print(f"  [{c}] {t[:110]}")
json.dump([{"c": c, "t": t} for c, t in new],
          open("tests/rules_new_candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n新增候选已存 tests/rules_new_candidates.json ({len(new)})")
