#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Armello 中文本地化 · 阶段1 初翻脚本（DeepSeek V4 Flash，非思考模式）

设计要点（防再次卡死 / 防烧钱 / 防破坏字符串）：
- 术语总表 glossary_master.json 渲染为 system prompt（跨批次命中 prompt 缓存，省钱）。
- 严格 EN→ZH 直译 + 结构化 JSON 输出 {"items":[{"id","zh"}]}，逐条对齐。
- 批量(默认25/批) + 并发(默认5) + 重试(3次) + 断点续跑(flash_out.jsonl)。
- 不把全量条目塞进任何 agent 上下文；这是独立离线脚本。
- 真实 token 计费汇总；生成三列对照 HTML 供人工审阅。

用法:
  python flash_translate.py --sample            # 跨类别代表性样本（看效果，默认）
  python flash_translate.py --all               # 全量 10,856 条初翻
  python flash_translate.py --prefix QUEST 50   # 指定类别前 N 条
"""
import csv, json, os, sys, time, html, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.abspath(__file__))
def _load_key():
    """key 来源优先级：环境变量 DEEPSEEK_API_KEY > api_key.local（git 忽略）。禁止硬编码入库。"""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
    local = os.path.join(ROOT, "api_key.local")
    if os.path.exists(local):
        with open(local, encoding="utf-8") as fp:
            key = fp.read().strip()
        if key:
            return key
    sys.exit("错误：未找到 key。请设置环境变量 DEEPSEEK_API_KEY 或创建 api_key.local（已被 .gitignore 忽略）")


KEY = _load_key()
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"
BATCH = 25
WORKERS = 5
OUT_JSONL = os.path.join(ROOT, "flash_out.jsonl")

# DeepSeek V4 Flash 计价（USD/百万token）；CNY 按 7.2 估算
PRICE = {"in": 0.14, "in_cache": 0.028, "out": 0.28}
USD2CNY = 7.2

# ---------- 加载术语总表 -> system prompt ----------
def build_system_prompt():
    g = json.load(open(os.path.join(ROOT, "glossary_master.json"), encoding="utf-8"))
    def kv(d): return "；".join(f"{k}={v}" for k, v in d.items() if not k.startswith("_"))
    parts = []
    parts.append("你是《Armello》桌游的简体中文本地化资深译者。把英文条目翻译成简体中文，忠实原文、术语统一、文笔自然。")
    parts.append("【四大属性】" + kv(g["attributes"]))
    parts.append("【资源】" + kv(g["resources"]))
    parts.append("【战斗机制】" + kv(g["combat_mechanics"]))
    parts.append("【状态】" + kv({k: v for k, v in g["statuses"].items() if not k.startswith("_")})
                 + "。" + g["statuses"]["_hud_rule"])
    parts.append("【世界/时间/地形】" + kv(g["world_terms"]) + "；" + kv(g["terrain"]))
    parts.append("【阵营/角色】" + kv(g["factions_roles"]))
    parts.append("【部族】" + g["clan_pattern"]["_rule"] + " " +
                 kv({k: v for k, v in g["clan_pattern"].items() if not k.startswith("_")}))
    parts.append("【英雄人名】" + kv(g["hero_names"]))
    parts.append("【Wyld系列】" + kv(g["wyld_series"]))
    parts.append("【BRW咒】" + kv(g["card_brw_curses"]))
    parts.append("【专有名词】" + kv(g["proper_nouns"]))
    parts.append("【翻译原则】" + " ".join(f"{i+1}.{p}" for i, p in enumerate(g["principles"])))
    parts.append("【标点】" + " ".join(g["punctuation"]))
    parts.append("【禁止翻译，原样保留】" + "；".join(g["do_not_translate"]["items"]))
    parts.append('【输出格式】只输出 JSON，不要任何解释或 markdown：'
                 '{"items":[{"id":"原ID","zh":"中文译文"}]}。逐条对应输入，数量一致。')
    return "\n".join(parts)

SYSTEM_PROMPT = build_system_prompt()

# ---------- 数据加载 ----------
def load_csv(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        r = csv.reader(f); next(r, None)
        for row in r:
            if len(row) >= 2 and row[0]:
                d[row[0]] = row[1]
    return d

# ---------- API ----------
def call_api(messages, max_tokens=4000, retries=3):
    body = {"model": MODEL, "messages": messages, "temperature": 0,
            "max_tokens": max_tokens, "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"}}
    data = json.dumps(body).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + "/chat/completions", data=data, method="POST")
            req.add_header("Authorization", "Bearer " + KEY)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"API failed after {retries} tries: {last!r}")

def parse_items(content):
    s = content.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"): s = s[4:]
    try:
        obj = json.loads(s)
    except Exception:
        a, b = s.find("{"), s.rfind("}")
        obj = json.loads(s[a:b+1])
    return {it["id"]: it["zh"] for it in obj.get("items", [])}

# ---------- 批处理 ----------
def translate_batch(batch):
    payload = [{"id": i, "en": en} for i, en in batch]
    msgs = [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "翻译以下条目：\n" + json.dumps(payload, ensure_ascii=False)}]
    resp = call_api(msgs)
    content = resp["choices"][0]["message"]["content"]
    items = parse_items(content)
    return items, resp.get("usage", {})

# ---------- 样本选择 ----------
def pick_sample(en):
    prefixes = ["ACCOLADE","ACH","CARD","HERO","TOOLTIP","UI","INV","QUEST",
                "CHATMESSAGE","GAMEGUIDEPAGE","DECL","ACT1","STATUSFEED","OPTIONS","TILENAME"]
    per = 8
    out, cnt = [], {p: 0 for p in prefixes}
    for i, text in en.items():
        if not text.strip(): continue
        p = i.split("_")[0]
        if p in cnt and cnt[p] < per:
            out.append((i, text)); cnt[p] += 1
    return out

def main():
    en = load_csv(os.path.join(ROOT, "English.csv"))
    cn = load_csv(os.path.join(ROOT, "SimplifiedChinese_modified.csv"))
    args = sys.argv[1:]
    if "--all" in args:
        targets = [(i, t) for i, t in en.items() if t.strip()]
        tag = "全量"
    elif "--prefix" in args:
        idx = args.index("--prefix"); pre = args[idx+1]; n = int(args[idx+2])
        targets = [(i, t) for i, t in en.items() if i.startswith(pre) and t.strip()][:n]
        tag = f"{pre} 前{n}"
    else:
        targets = pick_sample(en); tag = "代表性样本"

    # 断点续跑
    done = {}
    if os.path.exists(OUT_JSONL):
        for line in open(OUT_JSONL, encoding="utf-8"):
            try:
                o = json.loads(line); done[o["id"]] = o["zh"]
            except Exception: pass
    todo = [(i, t) for i, t in targets if i not in done]
    print(f"[{tag}] 目标 {len(targets)} 条，已完成 {len(targets)-len(todo)}，待翻 {len(todo)}")

    batches = [todo[i:i+BATCH] for i in range(0, len(todo), BATCH)]
    tot = {"in": 0, "in_cache": 0, "out": 0}
    results = dict(done)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(translate_batch, b): b for b in batches}
        with open(OUT_JSONL, "a", encoding="utf-8") as jf:
            for k, fut in enumerate(as_completed(futs), 1):
                try:
                    items, usage = fut.result()
                except Exception as e:
                    print("  批次失败:", e); continue
                for i, zh in items.items():
                    results[i] = zh
                    jf.write(json.dumps({"id": i, "zh": zh}, ensure_ascii=False) + "\n")
                jf.flush()
                ch = usage.get("prompt_cache_hit_tokens", 0)
                miss = usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0) - ch)
                tot["in_cache"] += ch; tot["in"] += miss; tot["out"] += usage.get("completion_tokens", 0)
                print(f"  批次 {k}/{len(batches)} ok | in_miss={miss} cache={ch} out={usage.get('completion_tokens',0)}")

    cost_usd = (tot["in"]*PRICE["in"] + tot["in_cache"]*PRICE["in_cache"] + tot["out"]*PRICE["out"]) / 1e6
    cost_cny = cost_usd * USD2CNY
    elapsed = time.time() - t0
    summary = {"tag": tag, "n_target": len(targets), "n_new": len(todo),
               "tokens": tot, "cost_usd": round(cost_usd, 4), "cost_cny": round(cost_cny, 4),
               "elapsed_s": round(elapsed, 1), "model": MODEL}
    print("==== 汇总 ====")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 生成审阅 HTML
    gen_review(targets, en, cn, results, summary)
    json.dump(summary, open(os.path.join(ROOT, "flash_run_summary.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

def gen_review(targets, en, cn, results, summary):
    rows = []
    changed = 0
    for i, _ in targets:
        e = en.get(i, ""); old = cn.get(i, ""); new = results.get(i, "")
        diff = (new.strip() != old.strip())
        if diff: changed += 1
        cls = "changed" if diff else ""
        rows.append(
            f'<tr class="{cls}"><td class="id">{html.escape(i)}</td>'
            f'<td class="en">{html.escape(e)}</td>'
            f'<td class="old">{html.escape(old)}</td>'
            f'<td class="new">{html.escape(new)}</td></tr>')
    s = summary
    meta = (f'模型 {s["model"]}（非思考）｜ 样本 {s["n_target"]} 条 ｜ 与现有不同 {changed} 条 ｜ '
            f'本次 token: 输入{s["tokens"]["in"]}(+缓存{s["tokens"]["in_cache"]}) / 输出{s["tokens"]["out"]} ｜ '
            f'本次花费 ≈ ${s["cost_usd"]} / ¥{s["cost_cny"]} ｜ 耗时 {s["elapsed_s"]}s')
    htmlpage = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>Armello Flash 初翻对照</title><style>
body{{font-family:"Microsoft YaHei",sans-serif;margin:0;background:#1e1e2e;color:#ddd}}
h1{{padding:14px 20px;margin:0;background:#11111b;color:#fff;font-size:17px}}
.meta{{padding:10px 20px;background:#181825;border-bottom:1px solid #313244;font-size:13px;color:#a6adc8}}
table{{width:100%;border-collapse:collapse;background:#1e1e2e}}
th,td{{border:1px solid #313244;padding:7px 10px;text-align:left;vertical-align:top;font-size:13px}}
th{{background:#11111b;color:#cdd6f4;position:sticky;top:0}}
td.id{{font-family:Consolas,monospace;font-size:11px;color:#6c7086;white-space:nowrap;max-width:170px;overflow:hidden}}
td.en{{color:#bac2de;width:30%}} td.old{{color:#f9b387;width:25%}} td.new{{color:#a6e3a1;width:30%;font-weight:500}}
tr.changed td.new{{background:#1d2b1d}}
tr:hover td{{background:#2a2a3c}}
</style></head><body>
<h1>Armello · Flash 初翻逐条对照（{summary['n_target']} 条 · 总表 v1.0 驱动）</h1>
<div class="meta">列：<b style="color:#bac2de">英文原文</b> ｜ <b style="color:#f9b387">现有译文</b> ｜ <b style="color:#a6e3a1">Flash 新译</b>（绿底=与现有不同）<br>{meta}</div>
<table><thead><tr><th>条目 ID</th><th>英文原文</th><th>现有译文</th><th>Flash 新译</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>"""
    open(os.path.join(ROOT, "review_flash.html"), "w", encoding="utf-8").write(htmlpage)
    print("已生成 review_flash.html")

if __name__ == "__main__":
    main()
