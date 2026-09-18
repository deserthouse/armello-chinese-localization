"""写入实验：v2 文楷图集 → gd 包（保存到临时文件，不碰游戏本体）。"""
import hashlib
import time

import numpy as np
import UnityPy
from PIL import Image

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
OUT = "fontwork/gd_write_test.unity3d"
V2 = "fontwork/menu_atlas_wenkai_v2.png"

v2_img = Image.open(V2)
assert v2_img.size == (2048, 2048) and v2_img.mode == "RGBA"
arr = np.array(v2_img)
gray = arr[:, :, 3]  # SDF 在 alpha
# 双通道冗余：RGB 与 A 都放 SDF，规避编码器取 L 还是 A 的不确定性
safe = np.dstack([gray, gray, gray, gray]).astype(np.uint8)
safe_img = Image.fromarray(safe, "RGBA")
v2_alpha_bytes = gray.tobytes()
print(f"v2 alpha: {len(v2_alpha_bytes)} bytes md5={hashlib.md5(v2_alpha_bytes).hexdigest()}")

t0 = time.time()
env = UnityPy.load(GD)
print(f"加载 {time.time()-t0:.0f}s")

obj_map = {}
for obj in env.objects:
    if obj.type.name in ("Texture2D", "MonoBehaviour"):
        try:
            nm = obj.read().m_Name or ""
        except Exception:
            continue
        obj_map.setdefault((nm, obj.type.name), obj)

atlas = obj_map[("NotoSansCJKsc-Regular SDF Atlas", "Texture2D")]
d = atlas.read()
orig_stream = (d.m_StreamData.path, d.m_StreamData.offset, d.m_StreamData.size)
print(f"原 stream: {orig_stream} fmt={d.m_TextureFormat}")

d.m_StreamData.path = ""
d.m_StreamData.offset = 0
d.m_StreamData.size = 0
d.set_image(safe_img)
d.save()  # 数据对象自带 save 写回 reader
print("set_image + save 完成")

t0 = time.time()
blob = env.file.save("original")
with open(OUT, "wb") as f:
    f.write(blob)
print(f"包保存 {time.time()-t0:.0f}s -> {OUT} ({len(blob)} bytes)")

# ---- 验证：回读临时文件 ----
env2 = UnityPy.load(OUT)
n_obj = len(list(env2.objects))
print(f"回读对象数: {n_obj}")
for want in (("NotoSansCJKsc-Regular SDF Atlas", "Texture2D"),
             ("NotoSansCJKtc-Bold SDF Atlas", "Texture2D"),
             ("NotoSansCJKjp-Bold SDF Atlas", "Texture2D")):
    for obj in env2.objects:
        if obj.type.name != "Texture2D":
            continue
        dd = obj.read()
        if dd.m_Name == want[0]:
            a = dd.image.tobytes()[3::4]
            tag = "sc(目标)" if "sc" in want[0] else "对照(应不变)"
            print(f"[{tag}] {want[0]}: md5={hashlib.md5(a).hexdigest()}"
                  f" {'✅==v2' if a == v2_alpha_bytes else ''}")
            break
