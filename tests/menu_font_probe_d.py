"""探针D：gamedatabase 当前 vs 备份——字符表与图集对拍。只读。"""
import hashlib
import struct

import UnityPy

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
GDB = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.backup"

MENU_CHARS = "卡牌图集开始设置继续退出选项成就部族领地收藏品鉴"
JIAN = 0x9274

def parse_char_table(raw, max_glyph=3000):
    best = (0, None)
    for start in range(256):
        n = (len(raw) - start) // 16
        if n < 1500:
            break
        ok = 0
        for i in range(min(n, 6000)):
            o = start + i * 16
            u, pad, g = struct.unpack_from("<IiI", raw, o)
            s = struct.unpack_from("<f", raw, o + 12)[0]
            if 0x20 <= u <= 0xFFFF and -1 <= pad <= 64 and g < max_glyph and 0.2 < s < 5.0:
                ok += 1
        if ok > best[0]:
            best = (ok, start)
    ok, start = best
    if ok < 1500:
        return None, (ok, start)
    n = (len(raw) - start) // 16
    table = {}
    for i in range(n):
        o = start + i * 16
        u, pad, g = struct.unpack_from("<IiI", raw, o)
        s = struct.unpack_from("<f", raw, o + 12)[0]
        if 0x20 <= u <= 0xFFFF and -1 <= pad <= 64 and g < max_glyph and 0.2 < s < 5.0:
            table[u] = g
    return table, (ok, start)

def probe(path, label):
    env = UnityPy.load(path)
    tmp = atlas = lang = None
    for obj in env.objects:
        if obj.type.name not in ("MonoBehaviour", "Texture2D"):
            continue
        try:
            nm = obj.read().m_Name or ""
        except Exception:
            continue
        if nm == "NotoSansCJKsc-Regular SDF" and obj.type.name == "MonoBehaviour":
            tmp = obj
        elif nm == "NotoSansCJKsc-Regular SDF Atlas":
            atlas = obj
        elif nm == "SimplifiedChinese" and obj.type.name == "MonoBehaviour":
            lang = obj
    print(f"\n===== {label} =====")
    table, cfg = parse_char_table(tmp.get_raw_data())
    if table is None:
        print(f"  字符表: 未解出 (best={cfg})")
        table = {}
    else:
        print(f"  字符表: {len(table)} 条 (best配置={cfg})")
        missing = [c for c in MENU_CHARS if ord(c) not in table]
        print(f"  菜单字: {'全部在场' if not missing else '缺失→ ' + ''.join(missing)}")
        print(f"  鉴 在表中: {JIAN in table}")
    d = atlas.read()
    alpha = d.image.tobytes()[3::4]
    print(f"  图集 alpha md5={hashlib.md5(alpha).hexdigest()}")
    return table, alpha

cur_t, cur_a = probe(GD, "gamedatabase 当前(9/17改写)")
bak_t, bak_a = probe(GDB, "gamedatabase 备份(9/11原始)")

print("\n图集 alpha 相同:", cur_a == bak_a)
if bak_t:
    only_cur = set(cur_t) - set(bak_t)
    only_bak = set(bak_t) - set(cur_t)
    print("表条目数: 当前", len(cur_t), "/ 备份", len(bak_t))
    print("仅当前有:", "".join(chr(u) for u in sorted(only_cur))[:80])
    print("仅备份有:", "".join(chr(u) for u in sorted(only_bak))[:80])
    # glyphIndex 是否变过（同字符指向是否被改动）
    moved = [chr(u) for u in sorted(set(cur_t) & set(bak_t)) if cur_t[u] != bak_t[u]]
    print("同字符 glyphIndex 被改:", len(moved), "".join(moved)[:80])
