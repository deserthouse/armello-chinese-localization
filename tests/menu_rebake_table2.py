"""重建步骤1c：全表解析 + 矩形表坐标约定交叉验证。只读。"""
import struct

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont

BASE = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
NOTO = "fontwork/noto_original.ttf"

env = UnityPy.load(BASE)
raw = alpha = None
for obj in env.objects:
    if obj.type.name == "MonoBehaviour" and (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF":
        raw = obj.get_raw_data()
    elif obj.type.name == "Texture2D" and (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
        alpha = np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)

def rec_ok(o):
    u = struct.unpack_from("<I", raw, o)[0]
    fx, fy, fw, fh = struct.unpack_from("<4f", raw, o + 4)
    return (0x20 <= u <= 0xFFFF and 0 <= fx < 2048 and 0 <= fy < 2048
            and 1 <= fw <= 90 and 1 <= fh <= 90)

# 从卡锚点双向扩展 36B 矩形表
anchor = 189360
start = anchor
while start - 36 >= 0 and rec_ok(start - 36):
    start -= 36
end = anchor
while end + 36 + 36 <= len(raw) and rec_ok(end + 36):
    end += 36
rects = {}
o = start
while o <= end and rec_ok(o):
    u = struct.unpack_from("<I", raw, o)[0]
    fx, fy, fw, fh, fox, foy, fadv, fscale = struct.unpack_from("<8f", raw, o + 4)
    if u not in rects:
        rects[u] = (fx, fy, fw, fh)
    o += 36
print(f"矩形表: {len(rects)} 条, 区间 [{start}, {end}]")

# 16B 字符表双向扩展
def crec_ok(o):
    u, g = struct.unpack_from("<II", raw, o)
    s = struct.unpack_from("<f", raw, o + 8)[0]
    return 0x20 <= u <= 0xFFFF and g < 2859 and 0.1 < s < 10.0

ca = 138048
cs = ca
while cs - 16 >= 0 and crec_ok(cs - 16):
    cs -= 16
ce = ca
while ce + 16 + 16 <= len(raw) and crec_ok(ce + 16):
    ce += 16
cmap = {}
o = cs
while o <= ce and crec_ok(o):
    u, g = struct.unpack_from("<II", raw, o)
    cmap[u] = g
    o += 16
print(f"字符表: {len(cmap)} 条, 区间 [{cs}, {ce}]")

# ---- 坐标约定验证：Noto 渲染 vs 图集格子 ----
font = ImageFont.truetype(NOTO, 160)

def render_mask(ch, bw, bh):
    img = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=font)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = min(bw / crop.shape[1], bh / crop.shape[0])
    nw, nh = max(1, int(crop.shape[1] * sc)), max(1, int(crop.shape[0] * sc))
    r = np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((nw, nh))) > 128
    cv = np.zeros((int(bh), int(bw)), bool)
    cv[(int(bh) - nh) // 2:(int(bh) - nh) // 2 + nh, (int(bw) - nw) // 2:(int(bw) - nw) // 2 + nw] = r
    return cv

def iou(a, b):
    u = a | b
    return (a & b).sum() / u.sum() if u.sum() else 0.0

MENU = "单人多人部族领地收藏品卡牌图集物品栏珠宝盒成就开始设置继续退出"
print("\n== 坐标验证（y 原样 vs 翻转）==")
plain, flip = [], []
for ch in MENU:
    u = ord(ch)
    if u not in rects:
        print(f"  {ch}: 不在表")
        continue
    fx, fy, fw, fh = rects[u]
    x0, y0 = int(round(fx)), int(round(fy))
    w, h = int(round(fw)), int(round(fh))
    r = render_mask(ch, w, h)
    if r is None:
        continue
    m1 = alpha[y0:y0 + h, x0:x0 + w] > 128
    y2 = 2048 - y0 - h
    m2 = alpha[y2:y2 + h, x0:x0 + w] > 128
    plain.append(iou(m1, r))
    flip.append(iou(m2, r))
    print(f"  {ch}: ({x0},{y0},{w},{h}) y原样={plain[-1]:.3f} y翻转={flip[-1]:.3f}")
print(f"均值: y原样={np.mean(plain):.3f} y翻转={np.mean(flip):.3f}")

import json
json.dump({hex(k): v for k, v in rects.items()}, open("fontwork/table_rect.json", "w"))
json.dump({hex(k): v for k, v in cmap.items()}, open("fontwork/table_char.json", "w"))
print("已存 fontwork/table_rect.json / table_char.json")
