"""prep5（写入前终验）：修正匹配器 → 2×2 身份矩阵 + 捐献格 + 数据块物理定位。只读。"""
import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
WK = "fontwork/LXGWWenKai-Regular.ttf"
NOTO = "fontwork/noto_original.ttf"

def load_alpha(path):
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
            return np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
    raise SystemExit("atlas not found")

gd = load_alpha(GD)
v2 = np.frombuffer(Image.open("fontwork/menu_atlas_wenkai_v2.png").tobytes()[3::4],
                   dtype=np.uint8).reshape(2048, 2048)

lab, _ = ndimage.label(gd > 100)
boxes = []
for s in ndimage.find_objects(lab):
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    if 12 <= (y1 - y0) < 80 and 12 <= (x1 - x0) < 80 and (y1 - y0) * (x1 - x0) > 150:
        boxes.append((x0, x1, y0, y1))
print(f"候选 blob: {len(boxes)}")

def render_mask(font_path, ch, box_w, box_h):
    """保持纵横比渲染到 box 大小画布内，居中。"""
    font = ImageFont.truetype(font_path, 160)
    img = Image.new("L", (360, 360), 0)
    ImageDraw.Draw(img).text((100, 90), ch, fill=255, font=font)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    gh, gw = crop.shape
    scale = min(box_w / gw, box_h / gh)
    nw, nh = max(1, int(gw * scale)), max(1, int(gh * scale))
    r = np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((nw, nh))) > 128
    canvas = np.zeros((box_h, box_w), bool)
    oy, ox = (box_h - nh) // 2, (box_w - nw) // 2
    canvas[oy:oy + nh, ox:ox + nw] = r
    return canvas

def shift_iou(a, b, r=3):
    best = 0.0
    H, W = a.shape
    bp = np.zeros((H + 2 * r, W + 2 * r), bool)
    bp[r:r + H, r:r + W] = b
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            bb = bp[r + dy:r + dy + H, r + dx:r + dx + W]
            u = a | bb
            if u.sum():
                best = max(best, (a & bb).sum() / u.sum())
    return best

def blob_mask(alpha, b):
    x0, x1, y0, y1 = b
    return alpha[y0:y1, x0:x1] > 128

def locate(ch, font_path, alpha):
    """用指定字体渲染在全部 blob 中找最佳格子（纵横比过滤 + 平移搜索）。"""
    best = (0.0, None, 0.0)
    for b in boxes:
        w, h = b[1] - b[0], b[3] - b[2]
        r = render_mask(font_path, ch, w, h)
        if r is None:
            continue
        s1 = shift_iou(blob_mask(alpha, b), r)
        if s1 > best[0]:
            best = (s1, b, 0)
    if best[1] is not None:
        b = best[1]
        w, h = b[1] - b[0], b[3] - b[2]
        r2 = render_mask(font_path, ch, w, h)
        second = shift_iou(blob_mask(alpha, b), r2)
    return best[0], best[1]

MENU = "卡牌图集开始设置继续退出成就"
print("\n== 2×2 身份矩阵（每字: v2格vs文楷 / v2格vsNoto | gd格vs文楷 / gd格vsNoto）==")
ok = 0
for ch in MENU:
    s, b = locate(ch, NOTO, gd)
    if b is None or s < 0.45:
        print(f"  {ch}: 定位失败 (best={s:.3f})")
        continue
    w, h = b[1] - b[0], b[3] - b[2]
    mv = blob_mask(v2, b)
    mg = blob_mask(gd, b)
    rw = render_mask(WK, ch, w, h)
    rn = render_mask(NOTO, ch, w, h)
    a = shift_iou(mv, rw)
    bb = shift_iou(mv, rn)
    c = shift_iou(mg, rw)
    d = shift_iou(mg, rn)
    verdict = "✓文楷" if a > bb and a > 0.45 else "✗"
    ok += verdict == "✓文楷"
    print(f"  {ch}: v2 {a:.3f}/{bb:.3f} | gd {c:.3f}/{d:.3f}  {verdict} (定位s={s:.3f})")
print(f"通过: {ok}/{len(MENU)}")

print("\n== 捐献格（党）==")
s, b = locate("党", NOTO, gd)
if b and s >= 0.45:
    w, h = b[1] - b[0], b[3] - b[2]
    print(f"党格 box={b} 定位s={s:.3f}")
    print(f"  v2(党格) vs 文楷鉴: {shift_iou(blob_mask(v2, b), render_mask(WK, '鉴', w, h)):.3f}")
    print(f"  v2(党格) vs 文楷党: {shift_iou(blob_mask(v2, b), render_mask(WK, '党', w, h)):.3f}")
else:
    print(f"党定位失败 best={s:.3f}")

print("\n== 数据块物理定位（gd 包文件内搜索原图集字节）==")
with open(GD, "rb") as f:
    data = f.read()
print(f"包文件大小: {len(data)}")
probe = gd.tobytes()
slice_mid = probe[2_000_000:2_040_000]
pos = data.find(slice_mid)
print(f"中段 40KB 切片命中: {pos}")
if pos != -1:
    start = pos - 2_000_000
    print(f"推定块起点: {start} | 验证全块: {data[start:start+4_194_304] == probe}")
