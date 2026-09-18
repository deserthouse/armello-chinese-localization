"""重建步骤2：从 WenKai TTF 全量重烘焙 sc 图集（清白画布+实测SDF剖面+6x超采样）。"""
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

WK = "fontwork/LXGWWenKai-Regular.ttf"
orig = np.load("fontwork/orig_alpha.npy")  # 原版 Noto 图集（PIL 朝向）
rects = {int(k, 16): v for k, v in json.load(open("fontwork/table_rect.json")).items()}
print(f"矩形表: {len(rects)} 条")

# ---- SDF 剖面实测 ----
ink = orig > 128
edt_in = ndimage.distance_transform_edt(ink)
edt_out = ndimage.distance_transform_edt(~ink)
prof_in, prof_out = {}, {}
sel = ink & (edt_in <= 4)
for y, x in zip(*np.where(sel & (np.random.rand(*ink.shape) < 0.02))):
    prof_in.setdefault(round(edt_in[y, x], 1), []).append(orig[y, x])
sel2 = (~ink) & (edt_out <= 14) & (edt_out >= 1)
for y, x in zip(*np.where(sel2 & (np.random.rand(*ink.shape) < 0.02))):
    prof_out.setdefault(int(edt_out[y, x]), []).append(orig[y, x])
print("内侧剖面:", {d: int(np.median(v)) for d, v in sorted(prof_in.items())[:6]})
print("外侧剖面:", {d: int(np.median(v)) for d, v in sorted(prof_out.items())[:14]})
K_IN = 20.0     # 由实测内插（d=1→138, d=1.4→146, d=2→151）
CAP_IN = 2.25   # (173-128)/20
def out_alpha(d):
    """实测两段：d=1→116, 2→94, 3→71, 4→51, 5→29, 6→3"""
    a = np.where(d <= 1, 128 - 12 * d, 116 - 22 * (d - 1))
    return np.clip(a, 0, 128)
MARGIN = 7      # 光晕外溢边距（原版光晕半径 ~6px 溢出矩形）

# ---- 覆盖检查：原版墨迹是否被表矩形全覆盖 ----
cover = np.zeros_like(ink)
for fx, fy, fw, fh in rects.values():
    x0, y0 = int(round(fx)), int(round(fy))
    x1, y1 = int(round(fx + fw)) + 3, int(round(fy + fh)) + 3
    cover[max(0, y0 - 3):min(2048, y1), max(0, x0 - 3):min(2048, x1)] = True
leftover = (orig > 60) & ~cover
print(f"原版墨迹未被矩形覆盖(>60): {leftover.sum()} px")

# ---- 烘焙 ----
font = ImageFont.truetype(WK, 160)
canvas = np.zeros((2048, 2048), dtype=np.uint8)
fail, done = [], 0
for u, (fx, fy, fw, fh) in rects.items():
    ch = chr(u)
    x0, y0 = int(round(fx)), int(round(fy))
    w, h = int(round(fw)), int(round(fh))
    if w < 2 or h < 2 or x0 < 0 or y0 < 0 or x0 + w > 2048 or y0 + h > 2048:
        fail.append((ch, "rect 越界"))
        continue
    img = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=font)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        fail.append((ch, "无字形"))
        continue
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # 6x 超采样+外溢边距：画布= (w+2M)x(h+2M)，字形按原 rect 内的相对位置放置
    W6, H6 = w * 6, h * 6
    sc = min(W6 / crop.shape[1], H6 / crop.shape[0])
    rw, rh = max(1, int(crop.shape[1] * sc)), max(1, int(crop.shape[0] * sc))
    big = np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((rw, rh), Image.LANCZOS)) > 128
    TW, TH = (w + 2 * MARGIN), (h + 2 * MARGIN)
    sup = np.zeros((TH * 6, TW * 6), bool)
    oy, ox = (h * 6 - rh) // 2, (w * 6 - rw) // 2
    sup[MARGIN * 6 + oy:MARGIN * 6 + oy + rh, MARGIN * 6 + ox:MARGIN * 6 + ox + rw] = big
    d_in = ndimage.distance_transform_edt(sup) / 6.0
    d_out = ndimage.distance_transform_edt(~sup) / 6.0
    a6 = np.where(sup,
                  np.clip(128 + K_IN * np.minimum(d_in, CAP_IN), 0, 173),
                  out_alpha(d_out))
    a6 = a6.reshape(TH, 6, TW, 6).mean(axis=(1, 3))
    tile = np.round(a6).astype(np.uint8)
    # 光晕外溢用 max 混合（避免抹掉邻字光晕）
    yy0, xx0 = max(0, y0 - MARGIN), max(0, x0 - MARGIN)
    yy1, xx1 = min(2048, y0 + h + MARGIN), min(2048, x0 + w + MARGIN)
    ty0, tx0 = yy0 - (y0 - MARGIN), xx0 - (x0 - MARGIN)
    region = tile[ty0:ty0 + (yy1 - yy0), tx0:tx0 + (xx1 - xx0)]
    canvas[yy0:yy1, xx0:xx1] = np.maximum(canvas[yy0:yy1, xx0:xx1], region)
    done += 1
print(f"烘焙: {done} 字, 失败 {len(fail)}: {fail[:10]}")

np.save("fontwork/new_alpha.npy", canvas)
Image.fromarray(canvas).save("fontwork/new_atlas_preview.png")
print(f"值域: {canvas.min()}..{canvas.max()} | 非零 {int((canvas>0).sum())} (原版 {int((orig>0).sum())})")

# ---- 自检：60 字抽样 IoU（新图集 vs WenKai 渲染 / vs Noto 渲染）----
rng = np.random.default_rng(7)
NOTO = "fontwork/noto_original.ttf"
def render_mask(path, ch, bw, bh):
    f = ImageFont.truetype(path, 160)
    img = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=f)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = min(bw / crop.shape[1], bh / crop.shape[0])
    rw, rh = max(1, int(crop.shape[1] * sc)), max(1, int(crop.shape[0] * sc))
    r = np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((rw, rh))) > 128
    cv = np.zeros((bh, bw), bool)
    cv[(bh - rh) // 2:(bh - rh) // 2 + rh, (bw - rw) // 2:(bw - rw) // 2 + rw] = r
    return cv

def iou(a, b):
    un = a | b
    return (a & b).sum() / un.sum() if un.sum() else 0.0

cjk = [u for u in rects if 0x4E00 <= u <= 0x9FFF]
sample = [ord(c) for c in "单人多人部族领地卡牌图集开始设置退出"] + list(rng.choice(cjk, 40, replace=False))
s_wk, s_nt = [], []
for u in sample:
    fx, fy, fw, fh = rects[u]
    x0, y0, w, h = int(round(fx)), int(round(fy)), int(round(fw)), int(round(fh))
    m = canvas[y0:y0 + h, x0:x0 + w] > 128
    rwk = render_mask(WK, chr(u), w, h)
    rnt = render_mask(NOTO, chr(u), w, h)
    if rwk is None:
        continue
    s_wk.append(iou(m, rwk))
    if rnt is not None:
        s_nt.append(iou(m, rnt))
print(f"抽样 {len(s_wk)}: 新图集vs文楷 IoU 均值 {np.mean(s_wk):.3f} 最低 {np.min(s_wk):.3f}")
print(f"            新图集vsNoto IoU 均值 {np.mean(s_nt):.3f}")
