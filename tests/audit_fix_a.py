"""A类批量修复：作用域限定替换 + 断言计数 + provenance 落痕。
用法: python tests/audit_fix_a.py dry   # 试运行（只报数）
     python tests/audit_fix_a.py run    # 执行并写回 master.jsonl
"""
import json
import re
import sys

DRY = (len(sys.argv) < 2 or sys.argv[1] != "run")
recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
LIT_N = "\\" + "n"

# ---- 专名变体（EN 作用域, 不区分大小写, 词边界）----
VARIANTS = [
    (r"Raven'?s Beak Dagger", {"乌鸦嘴匕首": "鸦喙匕首"}),
    (r"Masquerade Mask", {"伪装的面具": "易容面具", "伪装面具": "易容面具", "化妆舞会面具": "易容面具"}),
    (r"\bPoppet\b", {"巫毒人偶": "巫蛊娃娃", "巫毒娃娃": "巫蛊娃娃", "玩偶": "巫蛊娃娃"}),
    (r"Winged Boots", {"飞翼靴": "翅靴"}),
    (r"Mirror Cape", {"镜子斗篷": "镜影披风"}),
    (r"Moon Scythe", {"月之镰刀": "月亮镰刀"}),
    (r"coin master", {"硬币大师": "铸币大师"}),
    (r"\b[Ss]pymaster\b", {"王牌间谍": "间谍大师"}),
    (r"\bStrategist\b", {"谋士": "战略家"}),
    (r"Prestige Leader", {"声望领袖": "声望领先者"}),
    (r"\bprestige\b", {"威望": "声望"}),
    (r"\b[Ff]ollower", {"追随者": "随从"}),
    (r"\b[Tt]ile\b", {"方格": "地块"}),
]

# ---- 逐条格式修复（标记条目）----
PER_ID = {
    "CHATMESSAGE_GOFOR_REFLEXIVE_RABBIT02": [("锤!", "锤！")],
    "QUEST_BANDIT_3_10_QUESTINFODATA_ENCOUNTERTEXT": [(",他", "，他")],
    "QUEST_RAT_2_1_QUESTINFODATA_JOURNALRUMOURTEXT": [("了,", "了，")],
    "QUEST_RAT_2_3_QUESTINFODATA_ACTIONS_0_DEFAULTOUTCOME_JOURNALTEXT": [("阱!", "阱！")],
    "QUEST_RAT_2_7_QUESTINFODATA_JOURNALENCOUNTERTEXT": [("么?", "么？")],
    "QUEST_RAT_3_11_QUESTINFODATA_RUMOURTEXT": [("出!", "出！")],
    "QUEST_BANDIT_3_7_QUESTINFODATA_RUMOURTEXT": [(" -—", "——")],
    "QUEST_RABBIT_3_5_QUESTINFODATA_ENCOUNTERTEXT": [(" - ", "——")],
    "QUEST_BEAR_3_9_QUESTINFODATA_JOURNALENCOUNTERTEXT": [(" - ", "——")],
    "QUEST_RABBIT_3_8_QUESTINFODATA_JOURNALRUMOURTEXT": [(" - ", "——")],
    "QUEST_BANDIT_4_11_QUESTINFODATA_ACTIONS_3_ACTIONTEXT": [(">!", ">！")],
    "CARD_TRK38_STATUSFEEDPLAYEDTOTILE": [(".", "。")],
    "ACH_100_022_DESCRIPTION": [("最后1点", "最后 1 点")],
    "ACH_100_038_DESCRIPTION": [("降为0", "降为 0")],
    "ACH_100_041_DESCRIPTION": [("第5个", "第 5 个")],
    "ACH_100_042_DESCRIPTION": [("达到13点", "达到 13 点")],
    "CARD_ITM28_DESCRIPTION": [("+1爆发池", "+1 爆发池")],
    "CARD_MAG36_DESCRIPTION": [("生物+5生命", "生物 +5 生命")],
    "CARD_MAG28_DESCRIPTION": [("难度+1", "难度 +1")],
    "CARD_FOL13_DESCRIPTION": [("法术牌", "法术牌。")],
    "CHATMESSAGE_EXCLAIMOUCH_RABBIT02": [("啊唷！啊唷！真的很痛。哎呦……抽鼻涕。", "啊唷！啊唷！真的很痛。哎哟……吸了吸鼻子。")],
    "INV_AMULET06_DESCRIPTION": [("[c] 观察护身符 [/c]", "[c]观察护身符[/c]"), ("\n\n 遇到", "\n\n遇到"), ("\n\n 英雄护身符", "\n\n英雄护身符")],
    "SKEEVE_NOVELLA_03": [("你的库存", "你的物品栏")],
    "UI_PLAY_TO_BANE": [("给贝恩应用", "打给贝恩")],
    "CARD_BRW04_TARGETTEXT": [("给英雄应用", "打给英雄")],
    "CARD_BRW05_TARGETTEXT": [("给英雄应用", "打给英雄")],
    "ACCOLADE_MOSTGOLDEARNED": [("金手指", "点金手")],
    "GMCC_DEFAULT_KG_DESCRIPTION": [("精英国王守卫", "经典国王守卫")],
    "UI_CLANGROUNDS_TAB_LOADOUT": [("装载", "装备")],
}

stats = {}
changed = {}

def touch(rid, rule, old_zh, new_zh):
    stats[rule] = stats.get(rule, 0) + 1
    changed[rid] = (old_zh, new_zh, rule)

for r in recs:
    rid, en, zh = r["id"], r.get("en", ""), r.get("zh", "")
    if not zh:
        continue
    nz = zh
    # 1) 换行还原
    if LIT_N in en and "\n" in nz and LIT_N not in nz:
        nz2 = nz.replace("\n", LIT_N)
        if nz2 != nz:
            touch(rid, "换行还原", zh, nz2)
            nz = nz2
    # 2) [c] 空格/行首空格
    if re.search(r"\[c\] +| +\[/c\]|\n +[\u4e00-\u9fff]", nz):
        nz2 = re.sub(r"\[c\] +", "[c]", nz)
        nz2 = re.sub(r" +\[/c\]", "[/c]", nz2)
        nz2 = re.sub(r"\n +(?=[\u4e00-\u9fff\[])", "\n", nz2)
        if nz2 != nz:
            touch(rid, "[c]空格清理", zh, nz2)
            nz = nz2
    # 3) 专名变体（EN 作用域）
    for pat, mapping in VARIANTS:
        if re.search(r"(?<![A-Za-z])" + pat + r"(?![A-Za-z])", en, re.IGNORECASE):
            nz2 = nz
            for v, c in mapping.items():
                nz2 = nz2.replace(v, c)
            if nz2 != nz:
                touch(rid, f"专名:{list(mapping.values())[0]}", zh, nz2)
                nz = nz2
    # 4) 逐条格式
    if rid in PER_ID:
        nz2 = nz
        for old, new in PER_ID[rid]:
            if old in nz2:
                nz2 = nz2.replace(old, new)
        if nz2 != nz and nz2 != zh:
            touch(rid, f"per-id:{rid[:24]}", zh, nz2)
            nz = nz2
        elif nz == zh and nz2 != zh:
            touch(rid, f"per-id:{rid[:24]}", zh, nz2)
            nz = nz2
    # 5) 省略号（安全子集：仅当含 ... 或重复标点）
    if "..." in nz or "。。" in nz or "，，" in nz:
        nz2 = nz.replace("....", "……").replace("...", "……").replace("。。", "。").replace("，，", "，")
        if nz2 != nz:
            touch(rid, "省略号/重复标点", zh, nz2)
            nz = nz2
    # 6) NAME 条目裁决（Strategist/Armellian 等）
    if (rid.endswith("_NAME") or rid.endswith("_TITLE")) and en:
        if en == "Armellian" and "阿门罗公民" in nz:
            nz2 = nz.replace("阿门罗公民", "阿门罗人")
            touch(rid, "NAME裁决:Armellian", zh, nz2)
            nz = nz2

print(f"{'[DRY] ' if DRY else ''}变更条目 {len(changed)}")
for rule, n in sorted(stats.items(), key=lambda kv: -kv[1]):
    print(f"  {rule}: {n}")

if not DRY:
    ch_map = {rid: v for rid, v in changed.items()}
    out = []
    n_write = 0
    for r in recs:
        if r["id"] in ch_map:
            r["zh"] = ch_map[r["id"]][1]
            r.setdefault("provenance", []).append(
                {"r": "auditA", "by": "auto", "v": ch_map[r["id"]][2]})
            n_write += 1
        out.append(json.dumps(r, ensure_ascii=False) + "\n")
    open("master.jsonl", "w", encoding="utf-8").writelines(out)
    print(f"已写回 {n_write} 条")
    # 样例
    for rid, (o, n, rule) in list(ch_map.items())[:8]:
        print(f"  {rid} [{rule}]\n    旧: {o[:60]}\n    新: {n[:60]}")
