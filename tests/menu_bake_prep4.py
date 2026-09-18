"""prep4：四份图集的数值口径与布局互对（gd原版 / ra当前 / v1 / v2烘焙件）。只读。"""
import numpy as np
import UnityPy
from PIL import Image
from scipy import ndimage

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"

def load_alpha(path):
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        if (obj.read().m_Name or "") == "NotoSansCJKsc-Regular SDF Atlas":
            return np.frombuffer(obj.read().image.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)
    raise SystemExit("atlas not found")

def png_alpha(p):
    img = Image.open(p)
    return np.frombuffer(img.tobytes()[3::4], dtype=np.uint8).reshape(2048, 2048)

def stats(name, a):
    nz = a[a > 0]
    print(f"{name}: 非零 {nz.size} 像素 | 值域 {a.min()}..{a.max()} | "
          f"p50={np.percentile(nz, 50):.0f} p90={np.percentile(nz, 90):.0f} | 直方图[0,1-63,64-127,128-191,192-255]="
          f"{(a==0).sum()}, {((a>0)&(a<64)).sum()}, {((a>=64)&(a<128)).sum()}, {((a>=128)&(a<192)).sum()}, {(a>=192).sum()}")

def centers(a, thr):
    lab, _ = ndimage.label(a > thr)
    out = []
    for s in ndimage.find_objects(lab):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        if 2 <= (y1 - y0) < 90 and 2 <= (x1 - x0) < 90 and (y1 - y0) * (x1 - x0) > 25:
            out.append(((x0 + x1) // 2, (y0 + y1) // 2, x1 - x0, y1 - y0))
    return np.array([(c[0], c[1]) for c in out]), out

def align(name_a, ca, name_b, cb, tol=6):
    m = 0
    for c in ca:
        d = np.abs(cb - c).sum(axis=1)
        if d.min() <= tol:
            m += 1
    print(f"对齐 {name_a}→{name_b}: {m}/{len(ca)} (tol ±{tol}px)")

gd = load_alpha(GD)
ra = load_alpha(RA)
v1 = png_alpha("fontwork/menu_atlas_wenkai.png")
v2 = png_alpha("fontwork/menu_atlas_wenkai_v2.png")

for nm, a in (("gd原版", gd), ("ra当前", ra), ("v1烘焙件", v1), ("v2烘焙件", v2)):
    stats(nm, a)

for thr in (64, 100, 128):
    cg, _ = centers(gd, thr)
    cr, _ = centers(ra, thr)
    c1, _ = centers(v1, thr)
    c2, _ = centers(v2, thr)
    print(f"\n-- thr={thr}: blob数 gd={len(cg)} ra={len(cr)} v1={len(c1)} v2={len(c2)}")
    align("ra", cr, "gd", cg)
    align("v1", c1, "gd", cg)
    align("v2", c2, "gd", cg)
    align("v2", c2, "ra", cr)
