"""只读普查：构建根文件 + 前端相关 ResourceBundle + gamedatabase 中的字体类资产。
目的：核实"资产层已到头"结论的覆盖面——排查范围外的文件里还有没有 Font/TMP 资产。"""
import glob
import os
import sys

import UnityPy

DATA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data"
RB = os.path.join(DATA, "StreamingAssets", "ResourceBundles")

targets = sorted(glob.glob(os.path.join(DATA, "globalgamemanagers.assets")))
targets += sorted(glob.glob(os.path.join(DATA, "level[0-9]")))
targets += sorted(glob.glob(os.path.join(DATA, "sharedassets[0-9]*.assets")))
for name in ("frontend~2048x1536.unity3d", "mp_frontend~2048x1536.unity3d",
             "uitextures.unity3d", "vines_frontend~2048x1536.unity3d"):
    targets.append(os.path.join(RB, name))
targets += sorted(glob.glob(os.path.join(RB, "gamedatabase*.unity3d")))

KEYS = ("font", "sdf", "tmp", "noto", "arial", "liberation", "wenkai", "yahei")

for path in targets:
    short = os.path.basename(path)
    if not os.path.exists(path):
        print(f"[MISS] {short}")
        continue
    try:
        env = UnityPy.load(path)
    except Exception as e:
        print(f"[ERR ] {short}: {e}")
        continue
    counts = {}
    hits = []
    for obj in env.objects:
        t = obj.type.name
        counts[t] = counts.get(t, 0) + 1
        if t not in ("Font", "MonoBehaviour", "Texture2D", "Material"):
            continue
        try:
            name = obj.read().m_Name or ""
        except Exception:
            name = "<read-fail>"
        if any(k in name.lower() for k in KEYS):
            hits.append((t, name))
    total = sum(counts.values())
    mb = counts.get("MonoBehaviour", 0)
    font_n = counts.get("Font", 0)
    print(f"\n== {short}  objects={total} MB={mb} Font={font_n}")
    for t, name in sorted(set(hits)):
        print(f"   {t:14s} {name}")

print("\nDone.")
