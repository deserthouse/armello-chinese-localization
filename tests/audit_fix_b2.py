"""B类补充：BEAR_01 长文重写 + BANDIT_4_11 mighty 修复。"""
import json

LIT2 = "\\" + "n\\" + "n"
BEAR = (
    "在神圣的树林深处坐落着熊族的古老家园，这里生长着一丛圣树。萨娜尚是幼崽时，便被送进了这片温暖的怀抱。"
    "传说她由德鲁伊抚养长大，且是一个古老预言的主角。尽管起点如此崇高，她的生活却始终宁静而充满沉思。" + LIT2 +
    "对熊族而言，与怀尔德最契合的人肩负着照看族人成长的神圣职责。他们在冥想中寻找答案，"
    "以应对熊族乃至整个阿门罗面临的可怕威胁。于是，萨娜发觉自己被推上了守护全族的位置。" + LIT2 +
    "她发现了阿门罗有史以来最大的威胁——国王。那位曾团结诸族的高贵存在如今已成腐化的堡垒，"
    "化作萨娜的梦魇，驱使她踏上争夺王座之路，熊族的力量紧随其后。" + LIT2 +
    "森林姊妹萨娜是个爱好和平的存在。她天性倾心和平与怀尔德，这让她难以在血腥的王座之争中如鱼得水。"
    "但她依然坚持，决意履行族人与怀尔德托付给她的使命。" + LIT2 +
    "如今已然觉醒的熊族伟大守护者，将不惜一切守护怀尔德。"
)
BANDIT411_TAIL = "最终，你到达了顶峰。吟游诗人是对的。你强大无比。"

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
n = 0
for r in recs:
    if r["id"] == "UI_CLANGROUNDS_STORY_HERO_BEAR_01":
        assert LIT2 in r.get("en", ""), "EN 换行基准缺失"
        r["zh"] = BEAR
        r.setdefault("provenance", []).append(
            {"r": "auditB", "by": "agent", "v": "三方对照重写(官方与新译原句均破碎)"})
        n += 1
    if r["id"] == "QUEST_BANDIT_4_11_QUESTINFODATA_ACTIONS_3_DEFAULTOUTCOME_OUTCOMETEXT":
        zh = r.get("zh", "")
        old = "吟游诗人是对的。你太伟大了。"
        if old in zh:
            r["zh"] = zh.replace(old, BANDIT411_TAIL)
            r.setdefault("provenance", []).append(
                {"r": "auditB", "by": "agent", "v": "mighty=强大,伟大误译"})
            n += 1
        else:
            print("BANDIT_4_11 当前文:", zh[:80])
out = [json.dumps(r, ensure_ascii=False) + "\n" for r in recs]
open("master.jsonl", "w", encoding="utf-8").writelines(out)
print(f"补充修复 {n} 条")
