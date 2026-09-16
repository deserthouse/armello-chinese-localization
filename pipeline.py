#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Armello 中文本地化 · 条目状态机流水线（唯一入口）

架构：
  master.jsonl —— 唯一真源（每条一行，git 提供逐条 diff 历史）
  CSV / 审阅 HTML / 汉化补丁 —— 全部是可再生成的产物

条目状态机：
  untranslated  官中缺失/英文残留，待初翻（Flash 哨兵化）
  unaudited     官中存在但未经人工审阅，待级联仲裁（Flash 判官 → Pro 判官 → 人工）
  locked        R1~R4 已人工审计，锁定保护，任何自动流程禁止改动
  added         手工补齐的条目（无英文原文），视为已审定
  后续状态（Stage 2+ 写入）：arbitrated / escalated / human_ok / human_fixed

用法：
  python pipeline.py init      # 从三份 CSV 生成 master.jsonl + 分诊计数
  python pipeline.py stats     # 只读统计，不写文件
  python pipeline.py translate # Stage 1: Flash 初翻 untranslated 区（哨兵化保护，断点续跑）
  python pipeline.py review_split [N]  # Stage 3: 切审查批次文件（默认150条/批）到 review_batches/
  python pipeline.py review_merge      # Stage 3: 合并各批次判决到 master.jsonl
  python pipeline.py export    # Stage 4: QA 通过后导出 SimplifiedChinese_export.csv
"""
import csv
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, "master.jsonl")

EN_CSV = os.path.join(ROOT, "English.csv")
OFF_CSV = os.path.join(ROOT, "SimplifiedChinese.csv")
MOD_CSV = os.path.join(ROOT, "SimplifiedChinese_modified.csv")

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PLACE_RE = re.compile(r"\{\d+\}|%s|<[^<>\n]+>")
SENTINEL_FMT = "\u27e6{}\u27e7"  # ⟦0⟧
DRAFT_JSONL = os.path.join(ROOT, "draft_out.jsonl")

API_BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"
BATCH = 25
WORKERS = 5
PRICE = {"in": 0.14, "in_cache": 0.028, "out": 0.28}
USD2CNY = 7.2


def load_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
    local = os.path.join(ROOT, "api_key.local")
    if os.path.exists(local):
        with open(local, encoding="utf-8") as fp:
            key = fp.read().strip()
        if key:
            return key
    sys.exit("错误：未找到 key（DEEPSEEK_API_KEY 或 api_key.local）")


def load_master():
    recs = []
    with open(MASTER, encoding="utf-8") as fp:
        for line in fp:
            recs.append(json.loads(line))
    return recs


def save_master(recs):
    tmp = MASTER + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fp:
        for rec in recs:
            fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, MASTER)


def sentinel_encode(text):
    """占位符 -> ⟦n⟧ 哨兵。返回 (编码后文本, 哨兵列表)。哨兵跨翻译是确定性的。"""
    sentinels = []

    def sub(m):
        sentinels.append(m.group(0))
        return SENTINEL_FMT.format(len(sentinels) - 1)

    return PLACE_RE.sub(sub, text), sentinels


def sentinel_decode(text, sentinels):
    def sub(m):
        idx = int(m.group(1))
        return sentinels[idx] if idx < len(sentinels) else m.group(0)

    return re.sub(SENTINEL_FMT.format(r"(\d+)"), sub, text)


def build_system_prompt():
    g = json.load(open(os.path.join(ROOT, "glossary_master.json"), encoding="utf-8"))

    def kv(d):
        return "；".join(f"{k}={v}" for k, v in d.items() if not k.startswith("_"))

    parts = ["你是《Armello》桌游的简体中文本地化资深译者。把英文条目翻译成简体中文，忠实原文、术语统一、文笔自然。",
             "【四大属性】" + kv(g["attributes"]),
             "【资源】" + kv(g["resources"]),
             "【战斗机制】" + kv(g["combat_mechanics"]),
             "【状态】" + kv({k: v for k, v in g["statuses"].items() if not k.startswith("_")})
             + "。" + g["statuses"]["_hud_rule"],
             "【世界/时间/地形】" + kv(g["world_terms"]) + "；" + kv(g["terrain"]),
             "【阵营/角色】" + kv(g["factions_roles"]),
             "【部族】" + g["clan_pattern"]["_rule"] + " " +
             kv({k: v for k, v in g["clan_pattern"].items() if not k.startswith("_")}),
             "【英雄人名】" + kv(g["hero_names"]),
             "【Wyld系列】" + kv(g["wyld_series"]),
             "【BRW咒】" + kv(g["card_brw_curses"]),
             "【专有名词】" + kv(g["proper_nouns"]),
             "【翻译原则】" + " ".join(f"{i + 1}.{p}" for i, p in enumerate(g["principles"])),
             "【标点】" + " ".join(g["punctuation"]),
             "【禁止翻译，原样保留】" + "；".join(g["do_not_translate"]["items"]),
             "【哨兵】形如 ⟦数字⟧ 的记号是占位符哨兵，必须原样保留在译文中，位置符合语义。",
             '【输出格式】只输出 JSON：{"items":[{"id":"原ID","zh":"中文译文"}]}。逐条对应输入，数量一致。']
    return "\n".join(parts)


def call_api(key, messages, retries=3):
    body = {"model": MODEL, "messages": messages, "temperature": 0,
            "max_tokens": 4000, "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"}}
    data = json.dumps(body).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(API_BASE + "/chat/completions", data=data, method="POST")
            req.add_header("Authorization", "Bearer " + key)
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
        if s.lower().startswith("json"):
            s = s[4:]
    try:
        obj = json.loads(s)
    except Exception:
        a, b = s.find("{"), s.rfind("}")
        obj = json.loads(s[a:b + 1])
    return {it["id"]: it["zh"] for it in obj.get("items", [])}


def cmd_translate():
    key = load_key()
    sysp = build_system_prompt()
    recs = load_master()
    targets = [r for r in recs if r["status"] == "untranslated"]

    done = {}
    if os.path.exists(DRAFT_JSONL):
        with open(DRAFT_JSONL, encoding="utf-8") as fp:
            for line in fp:
                try:
                    o = json.loads(line)
                    done[o["id"]] = o["zh"]
                except Exception:
                    pass
    todo = [r for r in targets if r["id"] not in done]
    print(f"[Stage1 初翻] 目标 {len(targets)}，已完成 {len(done)}，待翻 {len(todo)}")

    # 哨兵编码
    enc = {}
    for r in todo:
        enc[r["id"]] = sentinel_encode(r["en"])

    def work(batch):
        payload = [{"id": r["id"], "en": enc[r["id"]][0]} for r in batch]
        msgs = [{"role": "system", "content": sysp},
                {"role": "user", "content": "翻译以下条目：\n" + json.dumps(payload, ensure_ascii=False)}]
        resp = call_api(key, msgs)
        items = parse_items(resp["choices"][0]["message"]["content"])
        usage = resp.get("usage", {})
        out = {}
        for r in batch:
            if r["id"] not in items:
                out[r["id"]] = None  # 缺失
                continue
            zh = items[r["id"]]
            # 哨兵校验+回填
            sent = enc[r["id"]][1]
            got = set(re.findall(SENTINEL_FMT.format(r"(\d+)"), zh))
            if got != {str(i) for i in range(len(sent))}:
                out[r["id"]] = None  # 哨兵不一致 -> 失败标记
            else:
                out[r["id"]] = sentinel_decode(zh, sent) if sent else zh
        return out, usage

    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    tot = {"in": 0, "in_cache": 0, "out": 0}
    fail_ids = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(work, b): b for b in batches}
        with open(DRAFT_JSONL, "a", encoding="utf-8") as jf:
            for k, fut in enumerate(as_completed(futs), 1):
                try:
                    items, usage = fut.result()
                except Exception as e:
                    print(f"  批次 {k} 整体失败: {e}")
                    for r in futs[fut]:
                        fail_ids.append(r["id"])
                    continue
                for rid, zh in items.items():
                    if zh is None:
                        fail_ids.append(rid)
                        continue
                    done[rid] = zh
                    jf.write(json.dumps({"id": rid, "zh": zh}, ensure_ascii=False) + "\n")
                jf.flush()
                ch = usage.get("prompt_cache_hit_tokens", 0)
                miss = usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0) - ch)
                tot["in_cache"] += ch
                tot["in"] += miss
                tot["out"] += usage.get("completion_tokens", 0)
                print(f"  批次 {k}/{len(batches)} ok")

    # 写回 master（zh_flash 字段，不动 zh；status -> flash_drafted）
    by_id = {r["id"]: r for r in recs}
    for rid, zh in done.items():
        r = by_id.get(rid)
        if r and r["status"] == "untranslated":
            r["zh_flash"] = zh
            r["status"] = "flash_drafted"
            r.setdefault("provenance", []).append({"r": "S1", "by": MODEL, "sentinel": "ok"})
    save_master(recs)

    cost_usd = (tot["in"] * PRICE["in"] + tot["in_cache"] * PRICE["in_cache"]
                + tot["out"] * PRICE["out"]) / 1e6
    summary = {"stage": "S1-translate", "n_target": len(targets), "n_ok": len(done),
               "n_fail": len(set(fail_ids)), "fail_ids": sorted(set(fail_ids))[:50],
               "tokens": tot, "cost_usd": round(cost_usd, 4),
               "cost_cny": round(cost_usd * USD2CNY, 4),
               "elapsed_s": round(time.time() - t0, 1), "model": MODEL}
    json.dump(summary, open(os.path.join(ROOT, "stage1_summary.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def read_csv_two_col(path, val_col):
    """读 ID,值 两列 CSV，返回 {id: value}；重复 id 以最后出现为准并告警。"""
    out = {}
    dup = []
    with open(path, encoding="utf-8-sig", newline="") as fp:
        reader = csv.reader(fp)
        header = next(reader)
        assert header[0].strip() == "ID", f"{path}: 意外表头 {header}"
        for row in reader:
            if not row or not row[0].strip():
                continue
            key = row[0].strip()
            val = row[1] if len(row) > 1 else ""
            if key in out:
                dup.append(key)
            out[key] = val
    if dup:
        print(f"[警告] {os.path.basename(path)} 有 {len(dup)} 个重复 ID（取末次出现）")
    return out


def classify(en, zh_official, zh):
    """分诊规则（Stage 0 静态派生，不调用任何 API）。"""
    if en is None:
        return "added"
    if zh == "" or (zh == en) or (not CJK_RE.search(zh)):
        return "untranslated"
    if zh != zh_official:
        return "locked"
    return "unaudited"


def cmd_init():
    en_map = read_csv_two_col(EN_CSV, "English")
    off_map = read_csv_two_col(OFF_CSV, "SimplifiedChinese")
    mod_map = read_csv_two_col(MOD_CSV, "SimplifiedChinese")

    all_ids = set(en_map) | set(off_map) | set(mod_map)
    only_off = set(off_map) - set(en_map)
    only_mod = set(mod_map) - set(en_map)
    if only_off:
        print(f"[警告] 官中独有 {len(only_off)} 条（英文源缺失），示例: {sorted(only_off)[:3]}")

    records = []
    stats = Counter()
    for rid in sorted(all_ids):
        en = en_map.get(rid)
        zh_off = off_map.get(rid, "")
        zh = mod_map.get(rid, "")
        status = classify(en, zh_off, zh)
        stats[status] += 1
        rec = {
            "id": rid,
            "en": en if en is not None else "",
            "zh_official": zh_off,
            "zh": zh,
            "status": status,
            "provenance": [],
        }
        if status == "locked":
            rec["provenance"].append({"r": "R1-R4", "by": "human-audit"})
        elif status == "added":
            rec["provenance"].append({"r": "data-fix-0623", "by": "human"})
        records.append(rec)

    with open(MASTER, "w", encoding="utf-8", newline="\n") as fp:
        for rec in records:
            fp.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nmaster.jsonl 已生成：{len(records)} 条")
    for k in ("locked", "unaudited", "untranslated", "added"):
        n = stats.get(k, 0)
        pct = n * 100.0 / len(records)
        print(f"  {k:<14} {n:>6}  ({pct:.1f}%)")

    # 未翻译/未审计区的前缀分布（后续阶段的攻坚地图）
    for zone in ("untranslated", "unaudited"):
        pref = Counter(r["id"].split("_")[0] for r in records if r["status"] == zone)
        top = ", ".join(f"{k}×{v}" for k, v in pref.most_common(8))
        print(f"\n[{zone}] 前缀 Top8: {top}")


REVIEW_DIR = os.path.join(ROOT, "review_batches")


def cmd_review_split(batch_size=150):
    """把 master 切成审查批次文件，每批一个 JSONL（id/en/zh_official/zh/zh_flash/context）。"""
    os.makedirs(REVIEW_DIR, exist_ok=True)
    recs = load_master()
    n = 0
    for i in range(0, len(recs), batch_size):
        n += 1
        path = os.path.join(REVIEW_DIR, f"batch_{n:03d}.jsonl")
        with open(path, "w", encoding="utf-8", newline="\n") as fp:
            for r in recs[i:i + batch_size]:
                fp.write(json.dumps({k: r.get(k, "") for k in
                                     ("id", "en", "zh_official", "zh", "zh_flash")},
                                    ensure_ascii=False) + "\n")
    print(f"已切 {n} 个批次文件 -> {REVIEW_DIR}/（每批 {batch_size} 条）")


def cmd_review_merge():
    """合并 review_batches/*_verdicts.jsonl 到 master.jsonl（可重复跑，已合并的自动跳过）。"""
    verdict_files = sorted(f for f in os.listdir(REVIEW_DIR) if f.endswith("_verdicts.jsonl"))
    if not verdict_files:
        sys.exit("无判决文件")
    recs = load_master()
    by_id = {r["id"]: r for r in recs}
    applied = Counter()
    skipped = Counter()
    for vf in verdict_files:
        with open(os.path.join(REVIEW_DIR, vf), encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    v = json.loads(line)
                except Exception:
                    skipped["bad_json"] += 1
                    continue
                rid = v.get("id")
                verdict = v.get("verdict")
                # 兼容人工终审页的 keep/edit 命名
                if verdict == "keep":
                    verdict = "ok"
                elif verdict == "edit":
                    verdict = "fix"
                r = by_id.get(rid)
                if r is None or verdict not in ("ok", "fix", "low_confidence"):
                    skipped["invalid"] += 1
                    continue
                new_zh = v.get("zh", "")
                if verdict == "fix":
                    if not new_zh.strip():
                        skipped["fix_no_zh"] += 1
                        continue
                    r["zh"] = new_zh
                r["status"] = {"ok": "reviewed_ok", "fix": "reviewed_fixed",
                               "low_confidence": "flagged"}[verdict]
                r.setdefault("provenance", []).append(
                    {"r": "S3", "by": v.get("by", "agent"), "v": verdict, "why": v.get("reason", "")[:120]})
                applied[verdict] += 1
    save_master(recs)
    print(f"合并完成: ok={applied['ok']} fix={applied['fix']} low_confidence={applied['low_confidence']} "
          f"跳过={dict(skipped) or '无'}")


def cmd_export():
    """Stage 4: 导出 modified CSV（两列：ID,SimplifiedChinese），QA 前置校验。"""
    PLACE_RE_QA = re.compile(r"\{\d+\}|%s|<[^<>\n]+>")
    problems = []
    recs = load_master()
    by_id = {r["id"]: r for r in recs}
    en_map = read_csv_two_col(EN_CSV, None)
    off_map = {r["id"]: r["zh_official"] for r in recs}
    # 直接以 master 为底（10,867 条全覆盖）
    out_rows = []
    for r in recs:
        rid = r["id"]
        zh = r["zh"]
        # QA-1: 占位符集合必须与英文原文一致（zh 与官中相同视为有官方先例，放行；EN 为空的补齐条目跳过）
        en = en_map.get(rid, "")
        if zh != off_map.get(rid) and en:
            if sorted(PLACE_RE_QA.findall(en)) != sorted(PLACE_RE_QA.findall(zh)):
                problems.append((rid, "占位符不一致"))
        # QA-2: 内部代号保护——官中保留英文(无汉字)的条目(骰子/皮肤/署名/DO NOT LOCALISE类)自动回退官中
        off = off_map.get(rid)
        if off is not None and not CJK_RE.search(off) and zh != off:
            r["zh"] = off
            r.setdefault("provenance", []).append({"r": "QA2", "by": "auto", "v": "revert_official"})
            print(f"  [QA2 回退] {rid}")
        out_rows.append((rid, zh))
    if problems:
        print(f"QA 未通过 {len(problems)} 条，不导出。前 10：")
        for rid, why in problems[:10]:
            print(f"  {rid}: {why}")
        sys.exit(1)
    path = os.path.join(ROOT, "SimplifiedChinese_export.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as fp:
        fp.write("ID,SimplifiedChinese\n")
        for rid, zh in out_rows:
            fp.write(f"{rid},{csv_quote(zh)}\n")
    print(f"QA 通过，已导出 {len(out_rows)} 条 -> {path}")
    # QA-3: 风格扫描报告（STYLE_GUIDE 存量清单的机器化；警告不阻塞导出）
    style = style_scan(recs)
    if style:
        print("\n[风格扫描] 存量警告（不阻塞导出，详见 STYLE_GUIDE.md 存量清单）：")
        for k, v in style:
            print(f"  {k}: {v}")


def style_scan(recs):
    """按 STYLE_GUIDE 规则扫描存量问题，返回 [(问题, 数量)]。"""
    out = []
    n_quotes = sum(1 for r in recs if '"' in re.sub(r'<[^<>]+>|\{\d+\}', '', r["zh"]))
    if n_quotes:
        out.append(("英文引号(应中文引号)", n_quotes))
    n_nin = sum(1 for r in recs if "您" in r["zh"])
    if n_nin:
        out.append(("\"您\"(应统一\"你\")", n_nin))
    n_half = sum(1 for r in recs if re.search(r'[\u4e00-\u9fff][,;:?!]|[,;:?!][\u4e00-\u9fff]', r["zh"]))
    if n_half:
        out.append(("半角标点紧邻中文", n_half))
    n_played = sum(1 for r in recs if "打出了" in r["zh"])
    if n_played:
        out.append(("状态反馈句\"打出了\"式(应\"对…施用\")", n_played))
    g = json.load(open(os.path.join(ROOT, "glossary_master.json"), encoding="utf-8"))
    for old in g.get("deprecated_variants", {}):
        if old.startswith("_"):
            continue
        n = sum(1 for r in recs if old in r["zh"])
        if n:
            out.append((f"废弃变体\"{old}\"", n))
    return out


def csv_quote(s):
    s = str(s)
    if any(c in s for c in ',"\n\r'):
        return '"' + s.replace('"', '""') + '"'
    return s


def cmd_stats():
    if not os.path.exists(MASTER):
        sys.exit("master.jsonl 不存在，先运行: python pipeline.py init")
    stats = Counter()
    pref_by_zone = {}
    with open(MASTER, encoding="utf-8") as fp:
        for line in fp:
            rec = json.loads(line)
            stats[rec["status"]] += 1
            if rec["status"] in ("untranslated", "unaudited", "escalated"):
                pref_by_zone.setdefault(rec["status"], Counter())[rec["id"].split("_")[0]] += 1
    total = sum(stats.values())
    print(f"master.jsonl 共 {total} 条")
    for k, v in stats.most_common():
        print(f"  {k:<14} {v:>6}  ({v * 100.0 / total:.1f}%)")
    for zone, pref in pref_by_zone.items():
        print(f"[{zone}] 前缀 Top8: {', '.join(f'{k}×{v}' for k, v in pref.most_common(8))}")


if __name__ == "__main__":
    cmds = {"init": cmd_init, "stats": cmd_stats, "translate": cmd_translate,
            "review_split": cmd_review_split, "review_merge": cmd_review_merge,
            "export": cmd_export}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "review_split":
        cmd_review_split(int(sys.argv[2]) if len(sys.argv) > 2 else 150)
    else:
        cmds[sys.argv[1]]()
