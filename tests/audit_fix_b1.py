"""B类修复（重建存档版）：三方对照重写 24 条。幂等可重放。"""
import json
import re

LIT2 = "\\" + "n\\" + "n"
FIX = {
 "CARD_TRK13_DESCRIPTION": "聚落每个黎明产出 +1 金币和 +1 声望，直到受到恐吓。",
 "CARD_TRK16_DESCRIPTION": "恐吓聚落并驱逐国王守卫。",
 "CARD_TRK37_DESCRIPTION": "安放<tooltip_sanctifiedwards>石阵结界</tooltip_sanctifiedwards>保护聚落，直到受到恐吓。",
 "QUEST_RABBIT_1_3_QUESTINFODATA_ACTIONS_1_DEFAULTOUTCOME_JOURNALTEXT":
   "<hero_name>行使国王总管的权力，确保囚犯获释。腐化之势暂被遏制。",
 "QUEST_ROT_3_4_QUESTINFODATA_ACTIONS_0_DEFAULTOUTCOME_OUTCOMETEXT":
   "你向腐化的中心伸出爪子。尖叫声萦绕于空中。腐化借助一道魔法回击。你倒下了，身负重伤。",
 "QUEST_WOLF_2_1_QUESTINFODATA_ACTIONS_1_DEFAULTOUTCOME_OUTCOMETEXT":
   "这场追逐持续得远比预想的长，但最终你还是跟丢了他们。你比自己以为的更强。",
 "QUEST_RABBIT_3_8_QUESTINFODATA_ACTIONS_4_DEFAULTOUTCOME_JOURNALTEXT":
   "那位曾经高贵的战士不愿堕入腐化。见到皇家旗帜后，他们神志清醒了几分，得以做出最后的牺牲。",
 "QUEST_BEAR_3_8_QUESTINFODATA_ACTIONS_3_DEFAULTOUTCOME_OUTCOMETEXT":
   "陌生人走上前来，眼中泛着微光。他在沉睡者的耳畔低语。你不知道他说了什么，但沉睡者猛地抽了口气，醒了过来。",
 "ENCOUNTER_GOBLINS_QUESTINFODATA_ACTIONS_2_DEFAULTOUTCOME_OUTCOMETEXT":
   "双爪伸出来。他们咆哮着。尖叫。“肉不肯玩！肉真坏！”他们掏出匕首，然后逃跑了。你孤身一个。他们走了。",
 "QUEST_WOLF_4_1_QUESTINFODATA_ACTIONS_2_ACTIONTEXT": "“我就爱痛痛快快打一场！把他们全杀光！”",
 "QUEST_BANDIT_2_10_QUESTINFODATA_RUMOURTEXT":
   "某个贸易者迷失在了平原上——这个可怜的傻瓜的马车陷进了泥地里。说不定是块好下手的肥肉！",
 "ENCOUNTER_ARMS_QUESTINFODATA_TITLE": "西米恩兵器铺",
 "ENCOUNTER_ARMS_QUESTINFODATA_TOOLTIPTEXT": "西米恩兵器铺开业大吉！",
 "CARD_TRK39_STATUSFEEDPLAYEDTOTILE": "<from_creature> 已召唤西米恩兵器铺至 <tile_name>。",
 "QUEST_RAT_2_4_QUESTINFODATA_ACTIONS_3_DEFAULTOUTCOME_JOURNALTEXT":
   "<hero_name>忠实的间谍大师很快查明商队的最终下场，并帮忙取走了留在附近的一件有用物品。",
 "UI_MULTIPLAYER_EVENTTIMER_ENDS": "距结束还有",
 "UI_PICK_RUMOUR_WARNING_3_6": "反正我也不需要你。",
 "QUEST_BEAR_3_9_QUESTINFODATA_JOURNALENCOUNTERTEXT":
   "我们的英雄登上峰顶，搜寻可能残存之物——任何尚能助他们完成使命的古代熊族圣物。",
 "QUEST_RAT_4_6_QUESTINFODATA_ACTIONS_0_TESTSUCCESSOUTCOME_OUTCOMETEXT":
   "怀尔德将天空染成血红。兔子和熊都被吓坏了，意识到也许怀尔德并不眷顾他们的联盟。",
 "ENCOUNTER_SWAMP_QUESTINFODATA_ENCOUNTERTEXT":
   "沼泽里的空气让你原本就已中毒而又吃力的呼吸更加迟滞。你倒在腐烂的原木前。起泡的唇间发出一声嘶哑的呱声：“不要抗拒毒液。它是份礼物。让我来告诉你……”",
 "QUEST_ROT_4_3_QUESTINFODATA_ACTIONS_3_ACTIONTEXT": "腐化你内心的怀尔德之性",
 "PROLOGUE_ACT1_OUTRO_1": "阿门罗腹地，黑暗蠢动" + LIT2 + "腐化凶兆，卷土重来",
 "PROLOGUE_ACT1_OUTRO_2": "猎狼受迫，暂且退走" + LIT2 + "鼠辈潜行，刺探虚实",
 "PROLOGUE_ACT2_OUTRO_2": "而东方骄阳之下" + LIT2 + "兔族追寻，就此启程",
}
PLACE = re.compile(r"\{\d+\}|%s|<[^<>\n]+>|\[[0-9A-Fa-f]{8}\]")
FIXTOK = {"<tile>": "<tile_name>", "<hero_name's>": "<hero_name>"}

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
n = 0
for r in recs:
    rid = r["id"]
    if rid in FIX:
        en, cand = r.get("en", ""), FIX[rid]
        e = sorted(FIXTOK.get(t, t) for t in PLACE.findall(en))
        z = sorted(PLACE.findall(cand))
        assert e == z, f"{rid} 占位符不符"
        if ("\\" + "n") in en:
            assert ("\\" + "n") in cand, f"{rid} 换行不符"
        if cand != r.get("zh"):
            r["zh"] = cand
            if not any(p.get("r") == "auditB" for p in r.get("provenance", [])):
                r.setdefault("provenance", []).append(
                    {"r": "auditB", "by": "agent", "v": "三方对照重写(重放)"})
            n += 1
out = [json.dumps(r, ensure_ascii=False) + "\n" for r in recs]
open("master.jsonl", "w", encoding="utf-8").writelines(out)
print(f"B1 重放 {n} 条变更")
