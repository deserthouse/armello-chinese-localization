"""审计 Phase0-A：确定性规则全库扫描（免费全覆盖机械错误类）。"""
import json
import re
import unicodedata

recs = [json.loads(l) for l in open("master.jsonl", encoding="utf-8")]
print(f"总条目 {len(recs)}")

PLACE = re.compile(r"\{\d+\}|%s|<[^<>\n]+>|\[[0-9A-Fa-f]{8}\]")
ALLOWED_LATIN = re.compile(r"^(/|B20A0EFF|A20A0EFF|F20A0EFF|000000FF|[-\s]*)[A-Za-z0-9_/&.:+-]*$")

findings = {}

def add(cls, rid, detail=""):
    findings.setdefault(cls, []).append((rid, detail))

CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b\u200c\u200d\ufeff]")

# 术语表加载（弃用变体）
deprecated = {}
for line in open("GLOSSARY.md", encoding="utf-8"):
    m = re.match(r"\|\s*([^|]+)\|\s*([^|]+)\|\s*\*\*([^*]+)\*\*", line)
    if m:
        pass
gloss = {}
try:
    gj = json.load(open("glossary_master.json", encoding="utf-8"))
    items = gj.items() if isinstance(gj, dict) else []
    for k, v in items:
        if isinstance(v, dict):
            for var in v.get("variants", []) if isinstance(v.get("variants"), list) else []:
                gloss.setdefault(var, str(v.get("canonical", k)))
        elif isinstance(v, str):
            gloss.setdefault(v, k)
except FileNotFoundError:
    print("!! glossary_master.json 不存在，术语扫描跳过")
print(f"术语表弃用变体 {len(gloss)} 条")

en_map = {}
import csv
with open("SimplifiedChinese_export.csv", encoding="utf-8-sig") as f:
    pass  # en 由 master 自带

zh_by_text = {}
for r in recs:
    rid, en, zh = r["id"], r.get("en", ""), r.get("zh", "")
    if not zh:
        add("空翻译", rid)
        continue
    # 1 控制符/零宽
    m = CTRL.search(zh)
    if m:
        add("控制/零宽字符", rid, f"U+{ord(m.group()):04X}")
    # 2 日式异体
    for bad, good in (("徳", "德"), ("剝", "剥"), ("壻", "婿"), ("涙", "泪")):
        if bad in zh:
            add("日式异体字", rid, f"{bad}→{good}")
    # 3 半角标点紧邻中文
    for m in re.finditer(r"[\u4e00-\u9fff][,;:!?]|[,;:!?][\u4e00-\u9fff]", zh):
        add("半角标点邻中文", rid, m.group())
        break
    # 4 英文残留（剥掉占位符/色码后仍有≥2连续字母且非白名单词）
    stripped = PLACE.sub("", zh)
    for m in re.finditer(r"[A-Za-z]{2,}", stripped):
        w = m.group()
        if w not in ("B", "FF", "AI"):
            add("英文字母残留", rid, w)
            break
    # 5 直引号
    if '"' in zh or ("'" in zh and not re.search(r"\w'\w", zh)):
        add("直引号", rid)
    # 6 省略号
    if "..." in zh or "。。" in zh or "，，" in zh:
        add("省略号/重复标点", rid)
    # 7 数字一致性（en 中的数字集合 vs zh）
    en_nums = set(re.findall(r"\d+", en))
    zh_nums = set(re.findall(r"\d+", zh))
    if en_nums and en_nums - zh_nums and not PLACE.search(en):
        miss = en_nums - zh_nums
        if not any(x in zh for x in miss):
            add("数字缺失", rid, f"en有{sorted(miss)} zh无")
    # 8 长度比异常
    if en and len(en) > 60 and len(zh) < len(en) * 0.15:
        add("疑似漏译(过短)", rid, f"en={len(en)} zh={len(zh)}")
    # 9 zh==en（英文原样）
    if zh == en and re.search(r"[A-Za-z]{3,}", en) and not re.search(r"[\u4e00-\u9fff]", zh):
        add("未翻译(=英文)", rid)
    # 10 中文间空格
    if re.search(r"[\u4e00-\u9fff] +[\u4e00-\u9fff]", zh):
        add("中文间空格", rid)
    # 11 括号配对
    if zh.count("（") != zh.count("）") or zh.count("(") != zh.count(")"):
        add("括号不配对", rid)
    # 12 术语弃用变体
    for var, canon in gloss.items():
        if var and var in zh:
            add("弃用术语变体", rid, f"{var}→{canon}")
            break
    # 13 风格残留
    if "打出了" in zh:
        add("打出了句式", rid)
    # 14 同文异源
    zh_by_text.setdefault(zh, []).append(rid)

for zh, ids in zh_by_text.items():
    if 2 <= len(ids) <= 8 and len(zh) >= 4:
        pass  # 同文复用在游戏文本中大量合法，仅在盲审层处理

print("\n== 扫描结果 ==")
for cls in sorted(findings, key=lambda k: -len(findings[k])):
    lst = findings[cls]
    print(f"\n[{cls}] {len(lst)} 条")
    for rid, d in lst[:6]:
        print(f"   {rid} {d}")

json.dump({k: v for k, v in findings.items()},
          open("tests/audit_scan_findings.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n明细已存 tests/audit_scan_findings.json")
