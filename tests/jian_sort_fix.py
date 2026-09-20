"""鉴字修复：对 TMP 字符表重排序（修复二分查找）。
根因：原地等长替换（党→鉴）破坏了表的 Unicode 升序，二分查找不到。
方案：读出全部 16B + 36B 记录 → 按 Unicode 重排 → 原路写回 → 重建包。
"""
import json
import struct

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from UnityPy.streams import EndianBinaryReader

BAK = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
RESS = "CAB-5755950a3e12e7650fb2d305a0af030e.resS"

# ---- 1) 读取基底，找到 TMP 资产 ----
env = UnityPy.load(BAK)
tmp_obj = None
off_atlas = None
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        d = obj.read()
        if d.m_Name == "NotoSansCJKsc-Regular SDF":
            tmp_obj = obj
    if obj.type.name == "Texture2D":
        d = obj.read()
        if d.m_Name == "NotoSansCJKsc-Regular SDF Atlas":
            off_atlas = d.m_StreamData.offset

raw = bytearray(tmp_obj.get_raw_data())
print(f"TMP raw: {len(raw)} bytes | atlas offset: {off_atlas}")

DANG, JIAN = 0x515A, 0x9274

# ---- 2) 读 16B 字符表 ----
c_start = 138048
c_recs = []
for i in range(2752):
    o = c_start + i * 16
    if o + 16 > len(raw):
        break
    u, g = struct.unpack_from("<II", raw, o)
    s, e = struct.unpack_from("<fI", raw, o + 8)
    c_recs.append((o, u, g, s, e))
valid_c = [(r, i) for i, r in enumerate(c_recs) if 0x20 <= r[1] <= 0xFFFF and r[2] < 2859 and 0.1 < r[3] < 10]
print(f"16B 表: {len(valid_c)} 有效记录")

# 找党的记录
dang_idx = next(i for r, i in valid_c if r[1] == DANG)
dang_off = c_recs[dang_idx][0]
dang_glyph = c_recs[dang_idx][2]
print(f"党: idx={dang_idx} offset={dang_off} glyph={dang_glyph}")

# 把党的 unicode 改成鉴（保留其他字段）
struct.pack_into("<I", raw, dang_off, JIAN)

# ---- 3) 读 36B 矩形表，同样替换 ----
r_anchor = 183960  # 党在 36B 表的记录起点
for i in range(2752):
    o = r_anchor + i * 36  # 不对——36B 表有自己的起始位置
# 找 36B 表中党的记录
r_start = None
for i in range(len(raw) // 36):
    o = i * 36
    if o + 36 > len(raw):
        break
    u = struct.unpack_from("<I", raw, o)[0]
    if u == DANG:
        fx, fy, fw, fh = struct.unpack_from("<4f", raw, o + 4)
        if 0 <= fx < 2048 and 0 <= fy < 2048 and 1 <= fw <= 90 and 1 <= fh <= 90:
            r_start = o
            print(f"36B 党记录: offset={o} rect=({fx:.0f},{fy:.0f},{fw:.0f},{fh:.0f})")
            break
if r_start is not None:
    struct.pack_into("<I", raw, r_start, JIAN)

# ---- 4) 重排序 16B 表 ----
# 读出全部有效记录 → 按 unicode 排序 → 写回
records = []
for i in range(2752):
    o = c_start + i * 16
    if o + 16 > len(raw):
        break
    u, g = struct.unpack_from("<II", raw, o)
    s, e = struct.unpack_from("<fI", raw, o + 8)
    if 0x20 <= u <= 0xFFFF and g < 2859 and 0.1 < s < 10:
        records.append((u, g, s, e))
records.sort(key=lambda x: x[0])
for i, (u, g, s, e) in enumerate(records):
    o = c_start + i * 16
    struct.pack_into("<II fI", raw, o, u, g, s, e)
print(f"16B 表已重排序（{len(records)} 条）")

# ---- 5) 重排序 36B 表 ----
# 找 36B 表的起始和 stride
r_table_start = None
r_records = []
for scan_start in range(100000, 200000, 36):
    ok = 0
    for i in range(100):
        o = scan_start + i * 36
        if o + 36 > len(raw):
            break
        u = struct.unpack_from("<I", raw, o)[0]
        fx, fy, fw, fh = struct.unpack_from("<4f", raw, o + 4)
        if 0x20 <= u <= 0xFFFF and 0 <= fx < 2048 and 0 <= fy < 2048 and 1 <= fw <= 90 and 1 <= fh <= 90:
            ok += 1
    if ok >= 90:
        r_table_start = scan_start
        break
print(f"36B 表起始: {r_table_start}")

if r_table_start:
    # 读全部记录
    for i in range(3000):
        o = r_table_start + i * 36
        if o + 36 > len(raw):
            break
        u = struct.unpack_from("<I", raw, o)[0]
        fx, fy, fw, fh = struct.unpack_from("<4f", raw, o + 4)
        rest = raw[o+20:o+36]
        if 0x20 <= u <= 0xFFFF and 0 <= fx < 2048 and 0 <= fy < 2048 and 1 <= fw <= 90 and 1 <= fh <= 90:
            r_records.append((u, fx, fy, fw, fh, bytes(rest), o))
    r_records.sort(key=lambda x: x[0])
    for i, (u, fx, fy, fw, fh, rest, _) in enumerate(r_records):
        o = r_table_start + i * 36
        struct.pack_into("<I", raw, o, u)
        struct.pack_into("<4f", raw, o + 4, fx, fy, fw, fh)
        raw[o+20:o+36] = rest
    print(f"36B 表已重排序（{len(r_records)} 条）")

# ---- 6) 写回 TMP 资产 + 图集 ----
tmp_obj.set_raw_data(bytes(raw))

# 图集：从已含鉴字的 WenKai 图集取
alpha_jian = np.load("fontwork/new_alpha_jian.npy")
block = alpha_jian[::-1].tobytes()

raw_ress = env.file.files[RESS].bytes
import hashlib
assert hashlib.md5(raw_ress[off_atlas:off_atlas+4194304]).hexdigest() == "f851f26e571700c2295da7d2e6cd9d28"
patched = raw_ress[:off_atlas] + block + raw_ress[off_atlas + 4194304:]
nr = EndianBinaryReader(patched)
nr.flags = env.file.files[RESS].flags
env.file.files[RESS] = nr
blob = env.file.save("original")
open("fontwork/gd_jian_sorted.unity3d", "wb").write(blob)
print(f"gd_jian_sorted 保存: {len(blob)} bytes")

# ---- 7) 验证 ----
env2 = UnityPy.load("fontwork/gd_jian_sorted.unity3d")
for obj in env2.objects:
    if obj.type.name == "MonoBehaviour":
        d = obj.read()
        if d.m_Name == "NotoSansCJKsc-Regular SDF":
            r2 = obj.get_raw_data()
            # 检查鉴在表中的位置是否正确（前一条 < 鉴 < 后一条）
            for i in range(2752):
                o = 138048 + i * 16
                if o + 16 > len(r2):
                    break
                u = struct.unpack_from("<I", r2, o)[0]
                if u == JIAN:
                    prev_u = struct.unpack_from("<I", r2, o - 16)[0] if o > 138048 else 0
                    next_u = struct.unpack_from("<I", r2, o + 16)[0] if o + 32 <= len(r2) else 0xFFFF
                    print(f"鉴在排序后位置: idx={i} U+{prev_u:04X} < 鉴(U+{JIAN:04X}) < U+{next_u:04X}")
                    print(f"排序正确: {prev_u < JIAN < next_u}")
                    break
