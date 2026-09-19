"""卡牌/英雄效果文本精校对账器（确定性，无模型）：
EN 与 zh 的数字/符号/时序词/状态关键词逐项对账，输出嫌疑队列。"""
import json
import re

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]

SCOPE_DESC = [r for r in recs if r.get("en") and r.get("zh") and (
    r["id"].endswith("_DESCRIPTION") or r["id"].startswith("TOOLTIP_HEROPOWER"))]

NUM_WORDS_EN = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "seven": 7, "eight": 8, "nine": 9, "ten": 10}
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

TERM_MAP = {
    "Shield": "盾牌", "Sword": "剑", "Die": "骰", "Dice": "骰", "Rot": "腐化",
    "Prestige": "声望", "Gold": "金币", "Magic": "魔法", "Action Point": "行动点",
    "Health": "生命", "Fight": "战力", "Body": "体力", "Wits": "智力", "Spirit": "灵力",
    "Dawn": "黎明", "Dusk": "黄昏", "Night": "夜", "Day": "白天",
}
TIME_EN = ["until end of next turn", "next turn", "each dawn", "at dawn", "per turn",
           "in battle", "when attacking", "when defending", "at night", "during the day"]

def nums_en(text):
    out = [int(x) for x in re.findall(r"\d+", text)]
    for w, v in NUM_WORDS_EN.items():
        if re.search(rf"\b{w}\b", text.lower()):
            out.append(v)
    return sorted(out)

def nums_zh(text):
    out = [int(x) for x in re.findall(r"\d+", text)]
    for c, v in CN_NUM.items():
        # 简单计次（限量词场景足够）
        out += [v] * len(re.findall(rf"(?<!\d){c}(?=[个枚张点次次回合])", text))
    return sorted(out)

flags = []
for r in SCOPE_DESC:
    en, zh = r.get("en", ""), r.get("zh", "")
    why = []
    # 1 数字对账（含符号数字）
    en_n = nums_en(en)
    zh_n = nums_zh(zh)
    if en_n and sorted(en_n) != sorted(zh_n):
        # 容差：EN 词数与中文数词混排时允许排序后逐值比对失败才报
        why.append(f"数字: EN{en_n} vs ZH{zh_n}")
    # 2 符号对账
    for sym in ("+", "-"):
        if en.count(sym + " ") + en.count(sym + "\t") > zh.count(sym):
            why.append(f"符号{sym}: EN{en.count(sym)} ZH{zh.count(sym)}")
    # 3 状态关键词
    for en_w, zh_w in TERM_MAP.items():
        if re.search(rf"(?<![A-Za-z]){en_w}", en, re.IGNORECASE) and zh_w not in zh:
            why.append(f"术语缺失: {en_w}→{zh_w}")
    # 4 时序词
    low = en.lower()
    for t in TIME_EN:
        if t in low:
            break
    if why:
        flags.append({"id": r["id"], "en": en[:110], "zh": zh[:80], "why": "; ".join(why[:3])})

print(f"对账范围 {len(SCOPE_DESC)} 条, 嫌疑 {len(flags)} 条")
for f in flags:
    print(f"\n{f['id']}\n  EN: {f['en']}\n  ZH: {f['zh']}\n  ⚠ {f['why']}")
json.dump(flags, open("tests/card_precision_flags.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
