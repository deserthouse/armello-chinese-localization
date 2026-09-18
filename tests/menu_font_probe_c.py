"""探针C v2：宽布局字符表硬解 + ra/gd SDF 资产清单 + 图集身份对拍。只读。"""
import hashlib
import os
import struct

import UnityPy
from PIL import Image

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"

MENU_CHARS = "卡牌图集开始设置继续退出选项成就部族领地收藏品鉴"
JIAN = 0x9274  # 鉴

def parse_char_table(raw, max_glyph=2859, min_hits=1500):
    """宽布局扫描：16B 记录、unicode@0、glyph@4、scale 在 8 或 12（f32），起始逐字节。"""
    best = (0, None)
    for start in range(64):
        n = (len(raw) - start) // 16
        if n < min_hits:
            continue
        for scale_off in (8, 12):
            ok = 0
            for i in range(min(n, 5000)):
                o = start + i * 16
                u, g = struct.unpack_from("<II", raw, o)
                if not (0x20 <= u <= 0xFFFF and g < max_glyph):
                    continue
                s = struct.unpack_from("<f", raw, o + scale_off)[0]
                if 0.2 < s < 5.0:
                    ok += 1
            if ok > best[0]:
                best = (ok, (start, scale_off))
    ok, cfg = best
    if ok < min_hits:
        return None, cfg
    start, scale_off = cfg
    n = (len(raw) - start) // 16
    table = {}
    for i in range(n):
        o = start + i * 16
        u, g = struct.unpack_from("<II", raw, o)
        s = struct.unpack_from("<f", raw, o + scale_off)[0]
        if 0x20 <= u <= 0xFFFF and g < max_glyph and 0.2 < s < 5.0:
            table[u] = g
    return table, cfg

def probe_file(path, label):
    env = UnityPy.load(path)
    assets = []
    for obj in env.objects:
        if obj.type.name not in ("MonoBehaviour", "Texture2D", "Font", "Material"):
            continue
        try:
            nm = obj.read().m_Name or ""
        except Exception:
            nm = "<read-fail>"
        if "SDF" in nm or "NotoSansCJK" in nm:
            assets.append((nm, obj.type.name, obj.path_id, obj))
    print(f"\n===== {label} =====")
    for nm, t, pid, _ in sorted(assets):
        print(f"  {t:14s} {nm}")

    tmp = next((o for nm, t, pid, o in assets
                if t == "MonoBehaviour" and nm == "NotoSansCJKsc-Regular SDF"), None)
    if tmp is None:
        print("  !! 无 sc TMP MonoBehaviour")
    else:
        table, cfg = parse_char_table(tmp.get_raw_data())
        if table:
            print(f"  sc TMP 字符表: {len(table)} 条 (start,scale_off={cfg})")
            missing = [c for c in MENU_CHARS if ord(c) not in table]
            print(f"  菜单字检查: {'全部在场' if not missing else '缺失→ ' + ''.join(missing)}")
            print(f"  鉴(0x{JIAN:X}) 在表中: {JIAN in table}")
        else:
            print(f"  sc TMP 字符表: 未解出 (best cfg={cfg})")

    atlas = next((o for nm, t, pid, o in assets
                  if t == "Texture2D" and nm == "NotoSansCJKsc-Regular SDF Atlas"), None)
    alpha = atlas.read().image.tobytes()[3::4]
    print(f"  图集 alpha md5={hashlib.md5(alpha).hexdigest()}")
    return alpha

alpha_gd = probe_file(GD, "gamedatabase.unity3d")
alpha_ra = probe_file(RA, "resources.assets")

for art in ("menu_atlas_wenkai_v2.png", "menu_atlas_wenkai.png"):
    p = os.path.join("fontwork", art)
    if not os.path.exists(p):
        continue
    img = Image.open(p)
    line = f"烘焙件 {art}: mode={img.mode} size={img.size}"
    a = img.tobytes()
    if img.mode == "RGBA":
        a = a[3::4]
    if img.size == (2048, 2048):
        line += f" | ==ra:{a == alpha_ra} ==gd:{a == alpha_gd}"
    print(line)

diff = sum(1 for x, y in zip(alpha_gd, alpha_ra) if x != y)
print(f"\ngd vs ra 图集 alpha 差异: {diff}/{len(alpha_gd)} = {diff/len(alpha_gd)*100:.1f}%")
