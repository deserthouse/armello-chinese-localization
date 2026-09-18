"""重建步骤1：权威 格子→字 映射（Noto渲染真值全库匹配）+ 原版SDF剖面实测。只读。"""
import json
import pickle

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

BASE = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
NOTO = "fontwork/noto_original.ttf"

env = UnityPy.load(BASE)
alpha = None
for obj in env.objects:
    if obj.type.name == "Texture2D":
        d = obj.read()
        if d.m_Name == "NotoSansCJKsc-Regular SDF Atlas":
            alpha = np.frombuffer(d.image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
assert alpha is not None
np.save("fontwork/orig_alpha.npy", alpha)
ink = alpha > 128

# ---- blob（>100 检出，行内合并）----
lab, _ = ndimage.label(alpha > 100)
boxes = []
for s in ndimage.find_objects(lab):
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    if 2 <= (y1 - y0) < 90 and 2 <= (x1 - x0) < 90 and (y1 - y0) * (x1 - x0) > 25:
        boxes.append((x0, x1, y0, y1))
boxes.sort(key=lambda b: (b[2] // 8, b[0]))
merged = []
for b in boxes:
    if merged and b[2] - merged[-1][3] < 6 and 0 <= b[0] - merged[-1][1] < 8 and b[0] - merged[-1][0] < 60:
        m = merged[-1]
        merged[-1] = (min(m[0], b[0]), max(m[1], b[1]), min(m[2], b[2]), max(m[3], b[3]))
    else:
        merged.append(list(b))
merged = [tuple(b) for b in merged if (b[1] - b[0]) < 90 and (b[3] - b[2]) < 90]
print(f"blob: {len(boxes)} → 合并 {len(merged)}")

# ---- Noto 渲染签名库 ----
order = json.load(open("fontwork/atlas_order.json", encoding="utf-8"))
font = ImageFont.truetype(NOTO, 160)

def render_tight(ch):
    img = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=font)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def sig(mask):
    """高度归一 24px、宽按比例，落 34x24 画布居中。"""
    h, w = mask.shape
    nh = 24
    nw = max(1, int(round(w * nh / h)))
    if nw > 32:
        return None
    r = np.array(Image.fromarray((mask * 255).astype(np.uint8)).resize((nw, nh))) > 128
    canvas = np.zeros((24, 34), bool)
    ox = (34 - nw) // 2
    canvas[:, ox:ox + nw] = r
    return canvas

char_data = {}  # ch -> (aspect, sigvec)
for ch in order:
    t = render_tight(ch)
    if t is None:
        continue
    s = sig(t)
    if s is None:
        continue
    char_data[ch] = (t.shape[1] / t.shape[0], s.astype(np.float32).ravel())
print(f"渲染签名: {len(char_data)} 字")

cands = list(char_data.items())
cand_asp = np.array([v[0] for _, v in cands])
cand_mat = np.stack([v[1] for _, v in cands])
cand_mat /= np.linalg.norm(cand_mat, axis=1, keepdims=True) + 1e-9

# ---- blob 匹配 ----
def blob_sig(b):
    x0, x1, y0, y1 = b
    m = ink[y0:y1, x0:x1]
    return sig(m)

mapping = {}
low_conf = []
for b in merged:
    x0, x1, y0, y1 = b
    w, h = x1 - x0, y1 - y0
    if h < 10 or w < 4:
        continue
    s = blob_sig(b)
    if s is None:
        continue
    v = s.astype(np.float32).ravel()
    v /= np.linalg.norm(v) + 1e-9
    sim = cand_mat @ v
    asp = w / h
    ok = np.abs(cand_asp - asp) / asp < 0.18
    sim = np.where(ok, sim, -1)
    top = np.argsort(sim)[::-1]
    ch1, s1 = cands[top[0]][0], sim[top[0]]
    ch2, s2 = cands[top[1]][0], sim[top[1]]
    if s1 - s2 > 0.06 and s1 > 0.55:
        mapping.setdefault(ch1, []).append((b, float(s1), float(s2)))
    else:
        low_conf.append((b, ch1, float(s1), float(s2)))

dup = {k: v for k, v in mapping.items() if len(v) > 1}
print(f"映射: {len(mapping)} 字 | 重复映射字: {len(dup)} | 低置信 blob: {len(low_conf)}")
MENU = "单人多人部族领地收藏品卡牌图集物品栏珠宝盒成就开始设置继续退出"
miss = [c for c in MENU if c not in mapping]
print(f"菜单字覆盖: {'全部✅' if not miss else '缺→' + ''.join(miss)}")
for c in dup:
    print(f"  重复 {c}: {[(b, round(s1,3)) for b, s1, s2 in dup[c]]}")

with open("fontwork/cell_map.json", "w", encoding="utf-8") as f:
    json.dump({ch: v[0][0] for ch, v in mapping.items() if len(v) == 1},
              f, ensure_ascii=False)
print("cell_map.json 已存（唯一映射）")

# ---- 原版 SDF 剖面实测：边缘处 alpha 随距离变化 ----
print("\n== SDF 剖面 ==")
edt_in = ndimage.distance_transform_edt(ink)
edt_out = ndimage.distance_transform_edt(~ink)
edge = (edt_in <= 1.5) & ink
d_in, a_in = [], []
for y, x in zip(*np.where(edge)[:4000]):
    d_in.append(edt_in[y, x])
    a_in.append(alpha[y, x])
inside_pts = list(zip(d_in, a_in))
# 外侧：距边缘 1..12px 的背景点
sel = (edt_out >= 1) & (edt_out <= 12) & (~ink) & (edt_in == 0)
for y, x in zip(*np.where(sel)[:8000]):
    d_in.append(edt_out[y, x])
    a_in.append(-float(alpha[y, x]))  # 负号=外侧
import collections
prof = collections.defaultdict(list)
for d, a in inside_pts:
    prof[round(d, 1)].append(a)
for dd in sorted(prof)[:14]:
    print(f"  内侧 d={dd}: alpha中位={np.median([a for a in prof[dd] if a > 0])}")
prof2 = collections.defaultdict(list)
for d, a in inside_pts:
    if a < 0:
        prof2[round(-d)].append(-a)
for dd in sorted(prof2)[:14]:
    print(f"  外侧 d={dd}: alpha中位={np.median(prof2[dd])}")
print("内侧最大值:", int(alpha[ink].max()))
