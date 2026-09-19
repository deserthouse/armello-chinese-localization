"""英雄+卡牌精校——仅一致性修复版（文学性改写已按用户指示全部撤回，移交 pro 接手）。幂等。"""
import json
import re

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]

# ---- 一致性名称修复（人名跨条目统一 / 称号格式统一 / 事实性错名）----
NAME_FIX = {
    "Magna, The Unbroken": "麦格纳，坚不可摧者",       # 与英雄名单"麦格纳"统一（旧译马格努斯）
    "Twiss, Little Lightpaw": "特维斯，小光爪",         # 与英雄名单"特维斯"统一
    "Sylas, Fisher of Souls": "塞拉斯，灵魂渔夫",       # 与英雄名单"塞拉斯"统一
    "Horace, The Iron Poet": "霍拉斯，硬铁诗人",        # 与英雄名单"霍拉斯"统一
    "Griotte, Butcher Baroness": "格莉奥特，屠夫女爵",   # 人名统一+称号格式统一
    "Yordana, The Devourer": "尤尔达娜，吞噬者",        # 称号格式统一（名前号后）
    "Hargrave, Thunder Earl": "哈格雷夫，雷霆伯爵",     # 同上
}
REF_SWEEP = [
    (r"The Unbroken", {"马格努斯": "麦格纳"}),
    (r"Fisher of Souls", {"西拉斯": "塞拉斯"}),
    (r"The Iron Poet", {"贺拉斯": "霍拉斯"}),
    (r"Butcher Baroness", {"格莱奥特": "格莉奥特"}),
]
# ---- 一致性/格式类文本修复 ----
PER_ID = {
    "INV_DICE_1017_BEARCLAN_DESCRIPTION": ("精神力量", "灵力即力量"),   # 与 DICE_1008 口号统一
    "INV_SIGNET10_DESCRIPTION": (" 在战斗中每杀掉一个对手， +2 魔法。", "战斗中每击杀一次 +2 魔法。"),  # 句式与 SIGNET11 统一
    "MAPPACK01_DLC_DESCRIPTION": ("季节皮——", "季节棋盘皮肤——"),      # 与商店条目"棋盘皮肤"统一
    "CARD_MAG26_DESCRIPTION": ("直到下一回合结束，智力+2。", "+2 智力，直到下一回合结束。"),  # 语序与同族卡统一
    "CARD_CON05_DESCRIPTION": ("战力 +1 ，智力 -1 ，直到下一回合结束。", "战力 +1，智力 -1，直到下一回合结束。"),  # 空格规范
}

n_name = n_ref = n_space = 0
for r in recs:
    en = r.get("en", "")
    if (r["id"].endswith("_NAME") or r["id"].endswith("_TITLE")) and en in NAME_FIX:
        if r.get("zh") != NAME_FIX[en]:
            r["zh"] = NAME_FIX[en]
            r.setdefault("provenance", []).append({"r": "jing-consistency", "by": "agent", "v": "一致性名称统一"})
            n_name += 1

for r in recs:
    en, zh = r.get("en", ""), r.get("zh", "")
    if not zh or r["id"].endswith(("_NAME", "_TITLE")):
        continue
    nz = zh
    for pat, mapping in REF_SWEEP:
        if re.search(r"(?<![A-Za-z])" + re.escape(pat) + r"(?![A-Za-z])", en, re.IGNORECASE):
            for old, new in mapping.items():
                nz = nz.replace(old, new)
    if r["id"] in PER_ID:
        old, new = PER_ID[r["id"]]
        nz = nz.replace(old, new)
    if nz != zh:
        r["zh"] = nz
        r.setdefault("provenance", []).append({"r": "jing-consistency", "by": "agent", "v": "一致性/格式"})
        n_ref += 1

for r in recs:
    zh = r.get("zh", "")
    if re.search(r"\n +[\u4e00-\u9fff\[]", zh):
        nz = re.sub(r"\n +(?=[\u4e00-\u9fff\[])", "\n", zh)
        if nz != zh:
            r["zh"] = nz
            r.setdefault("provenance", []).append({"r": "jing-consistency", "by": "agent", "v": "行首空格"})
            n_space += 1

out = [json.dumps(r, ensure_ascii=False) + "\n" for r in recs]
open("master.jsonl", "w", encoding="utf-8").writelines(out)
print(f"一致性修复: 名称 {n_name} / 文本 {n_ref} / 行首空格 {n_space}")
