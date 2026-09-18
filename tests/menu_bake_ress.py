"""resS 路线：包内 resS 等长原地覆写（对象不动）→ 临时文件验证。"""
import hashlib

import numpy as np
import UnityPy
from PIL import Image
from UnityPy.streams import EndianBinaryReader

BASE = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
OUT = "fontwork/gd_ress_test.unity3d"

# v2 烘焙件 alpha
v2 = np.array(Image.open("fontwork/menu_atlas_wenkai_v2.png"))
v2_alpha = v2[:, :, 3].tobytes()
assert len(v2_alpha) == 4194304

env = UnityPy.load(BASE)
f = env.file
RESS_NAME = "CAB-5755950a3e12e7650fb2d305a0af030e.resS"

# 从 BASE 现读 stream 偏移（不沿用历史值）
off = size = None
for obj in env.objects:
    if obj.type.name != "Texture2D":
        continue
    d = obj.read()
    if d.m_Name == "NotoSansCJKsc-Regular SDF Atlas":
        sd = d.m_StreamData
        assert sd.path.endswith(RESS_NAME), sd.path
        off, size = sd.offset, sd.size
print(f"stream: offset={off} size={size}")

ress = f.files[RESS_NAME]
assert isinstance(ress, EndianBinaryReader), type(ress)
raw = ress.bytes
print(f"resS 总长: {len(raw)}")
block = raw[off:off + size]
print(f"原块 md5: {hashlib.md5(block).hexdigest()} (翻转态, 应=f851f26e...)")
assert hashlib.md5(block).hexdigest() == "f851f26e571700c2295da7d2e6cd9d28", "原块不符，中止"

# v2 是左上原点 PNG；resS 块为左下原点（已实测 flipud），写入前垂直翻转
v2_arr = np.frombuffer(v2_alpha, dtype=np.uint8).reshape(2048, 2048)
v2_block = v2_arr[::-1].tobytes()
patched = raw[:off] + v2_block + raw[off + size:]
new_ress = EndianBinaryReader(patched)
new_ress.flags = ress.flags  # save_fs 无条件读取
f.files[RESS_NAME] = new_ress
blob = f.save("original")
open(OUT, "wb").write(blob)
print(f"保存: {OUT} ({len(blob)} bytes)")

# ---- 回读验证 ----
env2 = UnityPy.load(OUT)
n = len(list(env2.objects))
sc_md5 = None
for obj in env2.objects:
    if obj.type.name == "Texture2D":
        d = obj.read()
        if d.m_Name == "NotoSansCJKsc-Regular SDF Atlas":
            sd = d.m_StreamData
            assert sd.path.endswith(RESS_NAME), f"stream 变了: {sd.path}"
            sc_md5 = hashlib.md5(d.image.tobytes()[3::4]).hexdigest()
print(f"回读: 对象数={n} sc图集md5={sc_md5}")
print("✅ resS 路线验证通过" if n == 12046 and sc_md5 == "f43ee8d993ea50518c8026870b67a30d" else "❌")
