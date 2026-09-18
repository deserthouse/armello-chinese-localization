"""重建步骤1b：TMP 资产表硬解（最长连续合法段评分）+ Noto 渲染交叉验证。只读。"""
import struct

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont

BASE = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
NOTO = "fontwork/noto_original.ttf"

env = UnityPy.load(BASE)
tmp_raw = None
alpha = None
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF":
            tmp_raw = obj.get_raw_data()
    elif obj.type.name == "Texture2D":
        if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
            alpha = np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
assert tmp_raw is not None and alpha is not None
print(f"TMP raw: {len(tmp_raw)} bytes")

def run_len(valid_fn, start, width):
    n = (len(tmp_raw) - start) // width
    i = 0
    while i < n and valid_fn(start + i * width):
        i += 1
    return i

# ---- 布局A：16B 字符表 (unicode@0, glyph@4或8, scale f32@8或12) ----
best = (0, None)
for g_off in (4, 8):
    for s_off in (8, 12):
        if s_off == g_off:
            continue
        def valid(o, g_off=g_off, s_off=s_off):
            u, g = struct.unpack_from("<II", tmp_raw, o)
            if not (0x20 <= u <= 0xFFFF and g < 2859):
                return False
            s = struct.unpack_from("<f", tmp_raw, o + s_off)[0]
            return 0.1 < s < 10.0
        for start in range(0, 6000):
            r = run_len(valid, start, 16)
            if r > best[0]:
                best = (r, ("16B", start, g_off, s_off))
print(f"16B 字符表 best: run={best[0]} cfg={best[1]}")

# ---- 布局B：36B 矩形表 (unicode@0 + x,y,w,h) ----
best36 = (0, None)
for w_off in (4, 8):
    for y_off in (w_off + 4, ):
        def valid36(o, w_off=w_off, y_off=y_off):
            u = struct.unpack_from("<I", tmp_raw, o)[0]
            if not (0x20 <= u <= 0xFFFF):
                return False
            x, y, w, h = struct.unpack_from("<4i", tmp_raw, o + w_off)
            return 0 <= x < 2048 and 0 <= y < 2048 and 1 <= w <= 90 and 1 <= h <= 90
        for start in range(0, 6000):
            r = run_len(valid36, start, 36)
            if r > best36[0]:
                best36 = (r, ("36B", start, w_off, y_off))
print(f"36B 矩形表 best: run={best36[0]} cfg={best36[1]}")

# ---- 解码最优候选 ----
tables = {}
if best[0] >= 2000:
    _, start, g_off, s_off = best[1]
    n = run_len(lambda o: True, start, 16)  # placeholder
    i = 0
    cmap = {}
    while True:
        o = start + i * 16
        u, g = struct.unpack_from("<II", tmp_raw, o)
        s = struct.unpack_from("<f", tmp_raw, o + s_off)[0]
        if not (0x20 <= u <= 0xFFFF and g < 2859 and 0.1 < s < 10.0):
            break
        cmap[u] = g
        i += 1
    tables["char"] = cmap
    print(f"字符表解码: {len(cmap)} 条")
if best36[0] >= 2000:
    _, start, w_off, y_off = best36[1]
    i = 0
    rmap = {}
    while True:
        o = start + i * 36
        u = struct.unpack_from("<I", tmp_raw, o)[0]
        x, y, w, h = struct.unpack_from("<4i", tmp_raw, o + w_off)
        if not (0x20 <= u <= 0xFFFF and 0 <= x < 2048 and 0 <= y < 2048 and 1 <= w <= 90 and 1 <= h <= 90):
            break
        if u not in rmap:
            rmap[u] = (x, y, w, h)
        i += 1
    tables["rect"] = rmap
    print(f"矩形表解码: {len(rmap)} 条")

# ---- Noto 渲染交叉验证 ----
if "rect" in tables:
    rmap = tables["rect"]
    font = ImageFont.truetype(NOTO, 160)

    def render_mask(ch, bw, bh):
        img = Image.new("L", (420, 420), 0)
        ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=font)
        a = np.array(img) > 64
        ys, xs = np.where(a)
        crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        sc = min(bw / crop.shape[1], bh / crop.shape[0])
        nw, nh = max(1, int(crop.shape[1] * sc)), max(1, int(crop.shape[0] * sc))
        r = np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((nw, nh))) > 128
        cv = np.zeros((bh, bw), bool)
        cv[(bh - nh) // 2:(bh - nh) // 2 + nh, (bw - nw) // 2:(bw - nw) // 2 + nw] = r
        return cv

    def iou(a, b):
        u = a | b
        return (a & b).sum() / u.sum() if u.sum() else 0.0

    MENU = "单人多人部族领地收藏品卡牌图集物品栏珠宝盒成就开始设置继续退出"
    hit = tot = 0
    for ch in MENU:
        u = ord(ch)
        if u not in rmap:
            print(f"  {ch}: 不在矩形表")
            continue
        x, y, w, h = rmap[u]
        for flip in (False, True):
            yy = 2048 - y - h if flip else y
            m = alpha[yy:yy + h, x:x + w] > 128
            r = render_mask(ch, w, h)
            sc_ = iou(m, r)
            if sc_ > 0.45 or not flip:
                print(f"  {ch}: rect=({x},{y},{w},{h}) flip={flip} IoU={sc_:.3f}")
                if sc_ > 0.45:
                    hit += 1
                break
        tot += 1
    print(f"交叉验证: {hit}/{tot}")
    import json
    json.dump({hex(k): v for k, v in rmap.items()}, open("fontwork/table_rect.json", "w"))
    if "char" in tables:
        json.dump({hex(k): v for k, v in tables["char"].items()}, open("fontwork/table_char.json", "w"))
    print("表已存 fontwork/table_rect.json / table_char.json")
