"""审计 Phase0-B：分层大样本盲审（DeepSeek Pro，串行缓存友好）。"""
import json
import random
import re
import time
import urllib.request

random.seed(20260919)

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]

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

QUOTA = {"quests": 300, "cards": 280, "ui": 200, "encounters": 150,
         "items_ach": 120, "story": 90, "misc": 60}
pools = {}
for r in recs:
    pools.setdefault(strata(r["id"]), []).append(r)

sample = []
for k, q in QUOTA.items():
    pool = pools.get(k, [])
    sample += random.sample(pool, min(q, len(pool)))
random.shuffle(sample)
print(f"样本 {len(sample)} / {len(recs)}")
json.dump([r["id"] for r in sample], open("tests/audit_sample_ids.json", "w"))

GLOSS = open("GLOSSARY.md", encoding="utf-8").read()
STYLE = open("STYLE_GUIDE.md", encoding="utf-8").read()

SYS = f"""你是资深简体中文本地化审校，正在复审《Armello》(阿门罗) 桌游风电子游戏的民间重译补丁。
给你若干条目的英文原文与简中译文。这是一次【盲审】：你没有任何历史判决信息，只依据原文与规范独立判断。

【术语表】
{GLOSS}

【风格规范】
{STYLE}

【任务】逐条判断译文是否有问题。只输出有问题的条目，格式严格为每行一条：
行号|类别|简述问题|建议改法
类别只能是：术语错误|术语不一致|语义偏离|漏译/欠译|多译/添油加醋|风格不合规|标点或格式|错别字|生硬直译|其他
判断标准从严：玩家一眼能觉得别扭的都算。但不要为了找问题而找问题——译文忠实、通顺、符合术语表就是没问题，不要输出。
不要输出任何其他内容。"""

key = open("api_key.local").read().strip()
API = "https://api.deepseek.com/chat/completions"

def call(messages, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(
                API, data=json.dumps({
                    "model": "deepseek-v4-pro",
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "thinking": {"type": "enabled"},
                }).encode(), headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"], d.get("usage", {})
        except Exception as e:
            print(f"  重试{i}: {e}")
            time.sleep(5 * (i + 1))
    return None, {}

BATCH = 40
out = []
t0 = time.time()
for bi in range(0, len(sample), BATCH):
    batch = sample[bi:bi + BATCH]
    lines = [f"{i+1}|{r['id']}|{r.get('en','')}|{r.get('zh','')}" for i, r in enumerate(batch)]
    user = "\n".join(lines)
    content, usage = call([{"role": "system", "content": SYS},
                           {"role": "user", "content": user}])
    if content is None:
        print(f"批次 {bi//BATCH} 失败，跳过")
        continue
    flagged = 0
    for ln in content.strip().splitlines():
        ln = ln.strip()
        m = re.match(r"^(\d+)\|(.+)$", ln)
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(batch):
            out.append({"id": batch[idx]["id"], "flag": m.group(2),
                        "en": batch[idx].get("en", ""), "zh": batch[idx].get("zh", "")})
            flagged += 1
    print(f"批次{bi//BATCH+1:02d} {len(batch)}条 标记{flagged} 累计{len(out)} "
          f"tokens={usage.get('prompt_tokens','?')}/{usage.get('completion_tokens','?')} "
          f"{time.time()-t0:.0f}s")
    with open("tests/audit_blind_findings.jsonl", "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

print(f"\n完成: {len(out)} 条标记 / {len(sample)} 样本")
