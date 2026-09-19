"""二校（缺口二）：pro 引擎·绝对质量判尺·quests+encounters 层·三方拉通。
与一轮的差异：判尺=绝对质量（不因官中同样有错而放行）；规则=GLOSSARY v1.2 + STYLE_GUIDE 增补版。
"""
import argparse
import json
import re
import time
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="deepseek-v4-pro")
ap.add_argument("--think", default="1")
ap.add_argument("--dump", action="store_true")
args = ap.parse_args()

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
GLOSS = open("GLOSSARY.md", encoding="utf-8").read()
STYLE = open("STYLE_GUIDE.md", encoding="utf-8").read()
names = json.load(open("tests/glossary_names_v12.json", encoding="utf-8"))
NAME_LINES = "\n".join(f"{k} = {v['zh']}" for k, v in sorted(names.items()))

SYS = f"""你是《Armello》(阿门罗) 民间重译项目的二校终审。给你若干条目，每条格式：
[N] ID
EN: 英文原文
官: 官方中文（可能为"无"）
新: 我方现行译文
任务：**绝对质量审查**——不是与官中比较优劣，而是判断译文是否存在实质缺陷：语义偏差、漏译、错译、明显生硬影响理解、术语违规。即便译文与官中完全相同，只要存在上述缺陷就必须修。克制推理，直接给裁决。

【裁决格式】每条一行，制表符分隔：
N<TAB>KEEP
N<TAB>OFFICIAL<TAB>理由        （官中明显更好时采用官中）
N<TAB>REVISE<TAB>新译文<TAB>理由
RULE<TAB>类别<TAB>内容          （值得沉淀的规则）
不确定或仅是风味偏好差异选 KEEP。以下情形**不得**判 REVISE：纯文风偏好、修辞性改写、官中与新译各有千秋且新译无实质缺陷。

【格式铁律】占位符{{N}}/%s/<token>/[色码]逐字保留；EN 中的字面 \\n 转义保留为字面文本；台词引号随 EN；风味文（FLAVORTEXT）整体加“”。

【核心术语（含 v1.2 增补）】
{GLOSS}

【风格规范（含增补）】
{STYLE}

【专名表（强制一致）】
{NAME_LINES}"""

PLACE_RE = re.compile(r"\{\d+\}|%s|<[^<>\n]+>|\[[0-9A-Fa-f]{8}\]")
FIXTOK = {"<tile>": "<tile_name>", "<hero_name's>": "<hero_name>"}
LITN = "\\" + "n"

def guards(en, cand):
    e = sorted(FIXTOK.get(t, t) for t in PLACE_RE.findall(en))
    z = sorted(PLACE_RE.findall(cand))
    if e != z:
        return False
    if LITN in en and LITN not in cand:
        return False
    return True

key = open("api_key.local").read().strip()

def call(messages):
    for i in range(3):
        try:
            body = {"model": args.model, "messages": messages, "temperature": 0.2,
                    "max_tokens": 16000 if args.think == "1" else 8000,
                    "thinking": {"type": "enabled" if args.think == "1" else "disabled"}}
            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions", data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"], d.get("usage", {})
        except Exception as e:
            print(f"  重试{i}: {e}", flush=True)
            time.sleep(8 * (i + 1))
    return None, {}

judged = set()
try:
    for l in open("tests/pass2_log.jsonl", encoding="utf-8"):
        judged.add(json.loads(l)["id"])
except FileNotFoundError:
    pass
pool = [r for r in recs if r.get("en") and r.get("zh") and r["id"] not in judged]
print(f"二校范围 {len(pool)} 条", flush=True)
BATCH = 50
log = open("tests/pass3_log.jsonl", "a", encoding="utf-8")
rules = open("tests/pass3_rules.txt", "a", encoding="utf-8")
t0 = time.time()
TK = TO = TR = TS = 0
spent = 0.0

for bi in range(0, len(pool), BATCH):
    batch = pool[bi:bi + BATCH]
    lines = []
    for i, r in enumerate(batch):
        off = r.get("zh_official") or "无"
        esc = lambda s: s.replace("\n", "⏎").replace("\t", " ")
        lines.append(f"[{i+1}] {r['id']}\nEN: {esc(r.get('en',''))}\n官: {esc(off)}\n新: {esc(r.get('zh',''))}")
    content, usage = call([{"role": "system", "content": SYS},
                           {"role": "user", "content": "\n".join(lines)}])
    if content is None:
        print(f"批@{bi} 失败", flush=True)
        continue
    if args.dump:
        json.dump({"usage": usage, "content": content},
                  open("tests/pass2_dump.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        args.dump = False
    spent += (usage.get("prompt_tokens", 0) * 4.5 + usage.get("prompt_cache_hit_tokens", 0) * 0.15
              + usage.get("completion_tokens", 0) * 13.5) / 1e6
    b = {"KEEP": 0, "OFFICIAL": 0, "REVISE": 0, "SKIP": 0}
    for ln in content.splitlines():
        p = ln.split("\t")
        head = p[0].strip()
        if head == "RULE" and len(p) >= 3:
            rules.write(f"[{int(time.time())}] {p[1].strip()} | {' '.join(x.strip() for x in p[2:])}\n")
            rules.flush()
            continue
        m = re.match(r"^[\[\(\*\s]*(\d+)[\]\)\.\*\:\s]*$", head)
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if not (0 <= idx < len(batch)):
            continue
        r = batch[idx]
        verdict = p[1].strip().upper() if len(p) > 1 else "SKIP"
        if verdict not in b:
            verdict = "SKIP"
        note = ""
        new_zh = None
        if verdict == "REVISE" and len(p) >= 4:
            cand = "\t".join(p[2:-1]).replace("⏎", "\n").strip()
            note = p[-1].strip()[:80]
            if guards(r.get("en", ""), cand):
                new_zh = cand
            else:
                verdict, note = "SKIP", "守卫拦截"
        elif verdict == "OFFICIAL":
            off = r.get("zh_official") or ""
            if off and guards(r.get("en", ""), off):
                new_zh = off
                note = "采用官中"
            else:
                verdict, note = "KEEP", "官中格式问题"
        if new_zh is not None and new_zh != r.get("zh"):
            r["zh"] = new_zh
            r.setdefault("provenance", []).append(
                {"r": "pass2", "by": args.model, "v": f"{verdict}: {note}"})
        log.write(json.dumps({"id": r["id"], "v": verdict, "note": note,
                              "old": (r.get("zh") or "")[:60]}, ensure_ascii=False) + "\n")
        log.flush()
        b[verdict] += 1
    TK += b["KEEP"]; TO += b["OFFICIAL"]; TR += b["REVISE"]; TS += b["SKIP"]
    out = [json.dumps(r, ensure_ascii=False) + "\n" for r in recs]
    open("master.jsonl", "w", encoding="utf-8").writelines(out)
    print(f"批{bi//BATCH+1:03d} K{b['KEEP']}/O{b['OFFICIAL']}/R{b['REVISE']}/S{b['SKIP']} | "
          f"累计 K{TK}/O{TO}/R{TR}/S{TS} | ¥{spent:.2f} | {time.time()-t0:.0f}s", flush=True)

print(f"\n二校完成 K{TK}/O{TO}/R{TR}/S{TS} ¥{spent:.2f}", flush=True)
