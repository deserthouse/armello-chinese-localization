"""烘焙前置：解析 gd TMP 36B 矩形表 + 自动验证 ra 图集身份（文楷渲染 IoU 对拍）。只读。"""
import json
import struct

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"
WK = "fontwork/LXGWWenKai-Regular.ttf"

env = UnityPy.load(GD)
tmp_raw = atlas_alpha = None
for obj in env.objects:
    try:
        nm = obj.read().m_Name or ""
    except Exception:
        continue
    if nm == "NotoSansCJKsc-Regular SDF" and obj.type.name == "MonoBehaviour":
        tmp_raw = obj.get_raw_data()
    elif nm == "NotoSansCJKsc-Regular SDF Atlas" and obj.type.name == "Texture2D":
        atlas_alpha = np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
assert tmp_raw is not None and atlas_alpha is not None

# ---- 36B 矩形表硬解：unicode u32 + x,y i32 + w,h i32 + 4 度量 ----
best = (0, None)
for start in range(512):
    n = (len(tmp_raw) - start) // 36
    if n < 1000:
        break
    ok = 0
    for i in range(min(n, 1500)):
        o = start + i * 36
        u, x, y, w, h = struct.unpack_from("<Iiiii", tmp_raw, o)
        if 0x20 <= u <= 0xFFFF and 0 <= x < 2048 and 0 <= y < 2048 and 2 <= w <= 80 and 2 <= h <= 80:
            ok += 1
    if ok > best[0]:
        best = (ok, start)
ok, start = best
print(f"36B 表 best: {ok} 有效 / start={start}")
assert ok >= 1000, "矩形表未解出"

rects = {}
n = (len(tmp_raw) - start) // 36
for i in range(n):
    o = start + i * 36
    u, x, y, w, h = struct.unpack_from("<Iiiii", tmp_raw, o)
    if 0x20 <= u <= 0xFFFF and 0 <= x < 2048 and 0 <= y < 2048 and 2 <= w <= 80 and 2 <= h <= 80:
        if u not in rects:
            rects[u] = (x, y, w, h)
print(f"矩形表: {len(rects)} 条")

order = json.load(open("fontwork/atlas_order.json", encoding="utf-8"))
print("atlas_order:", len(order), "| 矩形交集:", sum(1 for c in order if ord(c) in rects))

# ---- ra 图集（候选文楷烘焙件） ----
env_ra = UnityPy.load(RA)
ra_alpha = None
for obj in env_ra.objects:
    if obj.type.name != "Texture2D":
        continue
    if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
        ra_alpha = np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
assert ra_alpha is not None

def cell_mask(alpha, r):
    x, y, w, h = r
    for oy in (0, 1):  # 尝试 y 原点两种朝向
        yy = y if oy == 0 else 2048 - y - h
        m = alpha[yy:yy + h, x:x + w] > 128
        if m.any():
            return m, oy
    return alpha[y:y + h, x:x + w] > 128, 0

# ---- 文楷渲染对拍 ----
def wk_mask(ch, w, h):
    font = ImageFont.truetype(WK, 200)
    img = Image.new("L", (400, 400), 0)
    ImageDraw.Draw(img).text((100, 100), ch, fill=255, font=font)
    a = np.array(img)
    ys, xs = np.where(a > 64)
    if len(ys) == 0:
        return np.zeros((h, w), bool)
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = np.array(Image.fromarray(crop).resize((w, h))) > 64
    return m

def iou(a, b):
    u = a | b
    return (a & b).sum() / u.sum() if u.sum() else 1.0

sample = [c for c in "卡牌图集开始设置继续退出选项成就部族领地收藏品" if ord(c) in rects]
rng = np.random.default_rng(42)
pool = [c for c in order if ord(c) in rects and 0x4E00 <= ord(c) <= 0x9FFF]
sample += list(rng.choice(pool, 24, replace=False))

oriens = {}
scores_ra, scores_gd = [], []
for ch in sample:
    r = rects[ord(ch)]
    w, h = r[2], r[3]
    wk = wk_mask(ch, w, h)
    m_ra, oy = cell_mask(ra_alpha, r)
    m_gd, _ = cell_mask(atlas_alpha, r)
    oriens[oy] = oriens.get(oy, 0) + 1
    scores_ra.append(iou(m_ra, wk))
    scores_gd.append(iou(m_gd, wk))

print(f"\n样本 {len(sample)} 字 | y朝向统计: {oriens}")
print(f"ra vs 文楷渲染 IoU: 均值 {np.mean(scores_ra):.3f} 中位 {np.median(scores_ra):.3f} 最低 {np.min(scores_ra):.3f}")
print(f"gd vs 文楷渲染 IoU: 均值 {np.mean(scores_gd):.3f} 中位 {np.median(scores_gd):.3f}")

# ---- 捐献格（党 index302）---- 
if ord("党") in rects:
    r = rects[ord("党")]
    m_ra, _ = cell_mask(ra_alpha, r)
    print(f"\n捐献格(党) ra vs 鉴-文楷 IoU: {iou(m_ra, wk_mask('鉴', r[2], r[3])):.3f}")
    print(f"捐献格(党) ra vs 党-文楷 IoU: {iou(m_ra, wk_mask('党', r[2], r[3])):.3f}")
    m_gd, _ = cell_mask(atlas_alpha, r)
    print(f"捐献格(党) gd(原版) vs 党-文楷 IoU: {iou(m_gd, wk_mask('党', r[2], r[3])):.3f}")

# ---- 空白格对齐 ----
mis = 0
for c in order:
    u = ord(c)
    if u not in rects:
        continue
    r = rects[u]
    g = cell_mask(atlas_alpha, r)[0]
    q = cell_mask(ra_alpha, r)[0]
    if g.any() != q.any():
        mis += 1
print(f"\n空白格不对齐数: {mis}/{len(order)}")
