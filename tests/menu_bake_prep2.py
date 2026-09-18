"""格子自识别：从 gd 原图集连通域导出槽位→字符映射，自动验证排列方向。只读。"""
import json

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"
WK = "fontwork/LXGWWenKai-Regular.ttf"

def load_alpha(path):
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
            return np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
    raise SystemExit("atlas not found")

gd = load_alpha(GD)
ra = load_alpha(RA)

def blobs(alpha, thr=100):
    lab, n = ndimage.label(alpha > thr)
    objs = ndimage.find_objects(lab)
    boxes = [(int(s.start), int(s.stop), int(t.start), int(t.stop)) for s, t in objs if objs is not None]
    boxes = [(x0, x1, y0, y1) for (y0, y1, x0, x1) in
             [(s[0].start, s[0].stop, s[1].start, s[1].stop) for s in objs]]
    boxes = [b for b in boxes if (b[1] - b[0]) * (b[3] - b[2]) > 30 and (b[1] - b[0]) < 90 and (b[3] - b[2]) < 90]
    return boxes

boxes_gd = blobs(gd)
print(f"gd 连通域: {len(boxes_gd)} 个")

# 网格拟合：原点聚类在 pitch 网格上
xs = sorted(set(b[0] for b in boxes_gd))
ys = sorted(set(b[2] for b in boxes_gd))
def cluster(v, tol=4):
    out, cur = [], [v[0]]
    for a in v[1:]:
        if a - cur[-1] <= tol:
            cur.append(a)
        else:
            out.append(int(np.mean(cur)))
            cur = [a]
    out.append(int(np.mean(cur)))
    return out
cols = cluster(xs)
rows = cluster(ys)
print(f"列原点数: {len(cols)} 行原点数: {len(rows)}")
print("列原点差分前10:", np.diff(cols)[:10])
print("行原点差分前10:", np.diff(rows)[:10])

def slot_of(b):
    def near(lst, v):
        best, bd = None, 10**9
        for i, c in enumerate(lst):
            d = abs(c - v)
            if d < bd:
                best, bd = i, d
        return best, bd
    ci, cd = near(cols, b[0])
    ri, rd = near(rows, b[2])
    return (ri, ci) if cd < 12 and rd < 12 else None

slots = {}
for b in boxes_gd:
    s = slot_of(b)
    if s:
        slots.setdefault(s, []).append(b)
print(f"落入槽位的连通域: {sum(len(v) for v in slots.values())} 个，非空槽: {len(slots)}")

order = json.load(open("fontwork/atlas_order.json", encoding="utf-8"))
NROWS, NCOLS = len(rows), len(cols)

def index_map(major):
    m = {}
    for (r, c), bb in slots.items():
        i = r * NCOLS + c if major == "row" else c * NROWS + r
        m[i] = (min(b[0] for b in bb), max(b[1] for b in bb), min(b[2] for b in bb), max(b[3] for b in bb))
    return m

def wk_mask(ch, w, h):
    font = ImageFont.truetype(WK, 200)
    img = Image.new("L", (400, 400), 0)
    ImageDraw.Draw(img).text((100, 100), ch, fill=255, font=font)
    a = np.array(img)
    ys_, xs_ = np.where(a > 64)
    if len(ys_) == 0:
        return None
    crop = a[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1]
    return np.array(Image.fromarray(crop).resize((max(w, 1), max(h, 1)))) > 64

def iou(a, b):
    u = a | b
    return (a & b).sum() / u.sum() if u.sum() else 1.0

def crop(alpha, box):
    x0, x1, y0, y1 = box
    return alpha[y0:y1, x0:x1] > 128

rng = np.random.default_rng(42)
pool = [i for i in range(len(order)) if i in index_map("row") and 0x4E00 <= ord(order[i]) <= 0x9FFF]
sample = rng.choice(pool, 30, replace=False)

for major in ("row", "col"):
    m = index_map(major)
    s_ra, s_gd = [], []
    for i in sample:
        ch = order[i]
        x0, x1, y0, y1 = m[i]
        wk = wk_mask(ch, x1 - x0, y1 - y0)
        if wk is None:
            continue
        s_ra.append(iou(crop(ra, m[i]), wk))
        s_gd.append(iou(crop(gd, m[i]), wk))
    print(f"\n[{major}-major] 样本{len(s_ra)}: ra-vs-文楷 IoU 均值 {np.mean(s_ra):.3f} | gd-vs-文楷 {np.mean(s_gd):.3f}")
