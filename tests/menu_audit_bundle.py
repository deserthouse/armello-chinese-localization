"""穷举审计：bak-preAtlas(旧干净版) vs 当前部署文件——逐对象原始字节哈希 + 块结构对比。只读。"""
import hashlib
import struct

import UnityPy
from UnityPy.streams import EndianBinaryReader

BAK = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d.bak-preAtlas"
LIVE = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"

def obj_hashes(path):
    env = UnityPy.load(path)
    out = {}
    for obj in env.objects:
        try:
            nm = obj.read().m_Name or ""
        except Exception:
            nm = "<read-fail>"
        out[(obj.path_id, obj.type.name, nm)] = hashlib.md5(obj.get_raw_data()).hexdigest()
    return out, env

hb, env_b = obj_hashes(BAK)
hl, env_l = obj_hashes(LIVE)
print(f"对象数: bak={len(hb)} live={len(hl)}")
only_b = set(hb) - set(hl)
only_l = set(hl) - set(hb)
print(f"仅bak有: {len(only_b)} | 仅live有: {len(only_l)}")
diff = [(k, hb[k], hl[k]) for k in set(hb) & set(hl) if hb[k] != hl[k]]
print(f"内容不同的对象: {len(diff)}")
for k, a, b in diff[:30]:
    print(f"  ≠ pid={k[0]} {k[1]} {k[2]!r}: {a[:8]} -> {b[:8]}")

# resS 条目字节级对比
RESS = "CAB-5755950a3e12e7650fb2d305a0af030e.resS"
rb = env_b.file.files[RESS].bytes
rl = env_l.file.files[RESS].bytes
print(f"\nresS: bak={len(rb)} live={len(rl)} 相同长度={len(rb)==len(rl)}")
if len(rb) == len(rl):
    diffmask = [i for i in range(0, len(rb), 65536) if rb[i:i+65536] != rl[i:i+65536]]
    print(f"64K 块级差异区间数: {len(diffmask)} (期望≈64 = 4MB 目标块)")

# 块结构对比（UnityFS header/blockinfo）
def blocks(path):
    with open(path, "rb") as f:
        data = f.read()
    sig = data[:7]
    ver = struct.unpack_from("<I", data, 12)[0] if sig == b"UnityFS" else None
    # 简化：只报文件级信息
    return sig, len(data)
print("\n文件级:", blocks(BAK), blocks(LIVE))

# Material 专项：SDF 材质的关键属性
for path, label in ((BAK, "bak"), (LIVE, "live")):
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        d = obj.read()
        if d.m_Name and "sc-Regular SDF" in d.m_Name:
            try:
                tt = obj.read_typetree()
                env_ = tt.get("m_SavedProperties", {}).get("m_TexEnvs", [])
                floats = tt.get("m_SavedProperties", {}).get("m_Floats", [])
                names = [e[0] for e in env_]
                print(f"\n[{label}] {d.m_Name}: texEnvs={names}")
                print(f"  floats={floats}")
            except Exception as e:
                print(f"[{label}] {d.m_Name}: typetree失败 {e}")
