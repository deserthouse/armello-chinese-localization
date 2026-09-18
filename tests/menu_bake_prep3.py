"""prep3：原版 Noto TTF 渲染真值 → 字→格定位 → ra 文楷身份对拍。只读。"""
import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

GDB = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.backup"
GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"

# 1) 从备份抽原版 Noto TTF
env = UnityPy.load(GDB)
noto_bytes = None
for obj in env.objects:
    if obj.type.name != "Font":
        continue
    d = obj.read()
    if d.m_Name == "NotoSansCJKsc-Regular":
        noto_bytes = bytes(d.m_FontData)
assert noto_bytes, "原版 Noto TTF 未找到"
open("fontwork/noto_original.ttf", "wb").write(noto_bytes)
print(f"原版 Noto TTF: {len(noto_bytes)} bytes")

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

# 2) gd 连通域（合并同格碎片）
lab, n = ndimage.label(gd > 100)
raw_boxes = []
for s in ndimage.find_objects(lab):
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    if 2 <= (y1 - y0) < 90 and 2 <= (x1 - x0) < 90 and (y1 - y0) * (x1 - x0) > 25:
        raw_boxes.append((x0, x1, y0, y1))
raw_boxes.sort(key=lambda b: (b[2] // 8, b[0]))
merged = []
for b in raw_boxes:
    if merged and b[2] - merged[-1][3] < 6 and abs(b[0] - merged[-1][0]) < 60:
        m = merged[-1]
        merged[-1] = (min(m[0], b[0]), max(m[1], b[1]), min(m[2], b[2]), max(m[3], b[3]))
    else:
        merged.append(b)
print(f"gd blob: 原 {len(raw_boxes)} → 合并 {len(merged)}")

# 3) 渲染真值与 IoU 工具
def render(font_path, ch, box_w, box_h):
    font = ImageFont.truetype(font_path, 200)
    img = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(img).text((110, 90), ch, fill=255, font=font)
    a = np.array(img) > 64
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if crop.shape[0] < 2 or crop.shape[1] < 2:
        return None
    return np.array(Image.fromarray((crop * 255).astype(np.uint8)).resize((box_w, box_h))) > 128

def iou(a, b):
    u = a | b
    return (a & b).sum() / u.sum() if u.sum() else 0.0

def blob_mask(alpha, b):
    x0, x1, y0, y1 = b
    return alpha[y0:y1, x0:x1] > 128

# 4) 定位：对每个目标字，用 Noto 渲染在全 blob 里找最佳格子
MENU = "卡牌图集开始设置继续退出选项成就部族领地收藏品"
targets = list(MENU) + ["党", "鉴"]

found = {}
for ch in targets:
    best = (0.0, None)
    for b in merged:
        w, h = b[1] - b[0], b[3] - b[2]
        if not (12 <= w <= 80 and 12 <= h <= 80):
            continue
        r = render("fontwork/noto_original.ttf", ch, w, h)
        if r is None:
            continue
        sc = iou(blob_mask(gd, b), r)
        if sc > best[0]:
            best = (sc, b)
    found[ch] = best
    print(f"  {ch}: Noto定位 IoU={best[0]:.3f} box={best[1]}")

# 5) 同格 ra 对文楷渲染
print("\n== ra 同格文楷对拍 ==")
s_ok, s_bad = [], []
for ch in MENU:
    sc, b = found[ch]
    if b is None or sc < 0.35:
        s_bad.append(ch)
        continue
    w, h = b[1] - b[0], b[3] - b[2]
    wk = render("fontwork/LXGWWenKai-Regular.ttf", ch, w, h)
    nt = render("fontwork/noto_original.ttf", ch, w, h)
    ra_iou = iou(blob_mask(ra, b), wk)
    gd_iou = iou(blob_mask(gd, b), wk)
    s_ok.append((ch, ra_iou, gd_iou))
    print(f"  {ch}: ra-vs-文楷 {ra_iou:.3f} | gd-vs-文楷 {gd_iou:.3f}")
if s_ok:
    arr = np.array([x[1] for x in s_ok])
    arr2 = np.array([x[2] for x in s_ok])
    print(f"均值: ra-vs-文楷 {arr.mean():.3f} / gd-vs-文楷 {arr2.mean():.3f}")
if s_bad:
    print("定位失败字:", "".join(s_bad))

# 6) 捐献格：党 的格子上 ra 是否变成鉴
sc, b = found["党"]
if b and sc >= 0.35:
    w, h = b[1] - b[0], b[3] - b[2]
    print(f"\n党格 box={b}")
    print(f"  ra(党格) vs 文楷鉴: {iou(blob_mask(ra, b), render('fontwork/LXGWWenKai-Regular.ttf', '鉴', w, h)):.3f}")
    print(f"  ra(党格) vs 文楷党: {iou(blob_mask(ra, b), render('fontwork/LXGWWenKai-Regular.ttf', '党', w, h)):.3f}")
    print(f"  gd(党格) vs Noto党: {iou(blob_mask(gd, b), render('fontwork/noto_original.ttf', '党', w, h)):.3f}")

# 7) 全局布局对齐：ra 与 gd 的 blob 位置一一对应
ra_lab, _ = ndimage.label(ra > 100)
ra_boxes = []
for s in ndimage.find_objects(ra_lab):
    y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
    if 2 <= (y1 - y0) < 90 and 2 <= (x1 - x0) < 90 and (y1 - y0) * (x1 - x0) > 25:
        ra_boxes.append(((x0 + x1) // 2, (y0 + y1) // 2))
gd_centers = np.array([((b[0] + b[1]) // 2, (b[2] + b[3]) // 2) for b in merged])
match, far = 0, 0
for c in ra_boxes:
    d = np.abs(gd_centers - np.array(c)).sum(axis=1)
    if d.min() <= 3:
        match += 1
    else:
        far += 1
print(f"\n布局对齐: ra blob {len(ra_boxes)} 个，中心±3px 匹配 {match}，无匹配 {far}")
