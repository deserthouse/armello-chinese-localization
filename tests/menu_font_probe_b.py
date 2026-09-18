"""探针B：SimplifiedChinese 语言绑定对象解析 + 三处 sc SDF 图集像素对比。只读。"""
import hashlib
import io
import re
import struct

import UnityPy

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
RA = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"
RAB = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets.backup"

# ---------- 1) gamedatabase：语言对象群 + SimplifiedChinese 原始解析 ----------
env = UnityPy.load(GD)
objs = list(env.objects)

lang_names = ("SimplifiedChinese", "TraditionalChinese", "English", "Japanese", "Korean",
              "French", "German", "Spanish", "Italian", "Russian", "Portuguese", "Polish",
              "Chinese", "Language")
lang_objs = {}
for obj in objs:
    if obj.type.name != "MonoBehaviour":
        continue
    try:
        nm = obj.read().m_Name or ""
    except Exception:
        continue
    if nm and any(nm == x or nm.startswith(x) for x in lang_names):
        lang_objs[nm] = obj

print("-- language-ish MonoBehaviours --")
for nm, obj in sorted(lang_objs.items()):
    print(f"  pid={obj.path_id:<22} {nm}")

sc = lang_objs.get("SimplifiedChinese")
if sc:
    raw = sc.get_raw_data()
    print(f"\nSimplifiedChinese raw size={len(raw)}")
    # 可读字符串
    strs = re.findall(rb"[\x20-\x7e]{4,}", raw)
    print("strings:", [s.decode() for s in strs][:20])
    # PPtr 模式：fileID(i32)+pathID(i64)，fileID 通常 0（同文件）
    pids = {}
    for i in range(len(raw) - 12):
        fid, pid = struct.unpack_from("<iq", raw, i)
        if fid == 0 and pid != 0 and abs(pid) > 10**15:
            pids[pid] = i
    name_by_pid = {}
    for obj in objs:
        try:
            name_by_pid[obj.path_id] = (obj.type.name, obj.read().m_Name or "")
        except Exception:
            pass
    print("same-file PPtr candidates:")
    for pid, off in pids.items():
        t, nm = name_by_pid.get(pid, ("?", "?"))
        if t != "?":
            print(f"  off={off:6d} -> {t:14s} {nm!r}")

# ---------- 2) 三处 sc 图集像素哈希 ----------
def atlas_digest(env, label):
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        try:
            d = obj.read()
        except Exception:
            continue
        if d.m_Name == "NotoSansCJKsc-Regular SDF Atlas":
            sd = getattr(d, "m_StreamData", None)
            print(f"\n[{label}] pid={obj.path_id} size={d.m_Width}x{d.m_Height} fmt={d.m_TextureFormat}"
                  f" stream={(sd.path, sd.offset, sd.size) if sd else None}")
            img = d.image
            b = img.tobytes()
            print(f"  mode={img.mode} bytes={len(b)} md5={hashlib.md5(b).hexdigest()}")
            img.convert("L").save(f"fontwork/probe_atlas_{label}.png")
            return
    print(f"\n[{label}] sc atlas NOT FOUND")

atlas_digest(UnityPy.load(GD), "gd_current")
atlas_digest(UnityPy.load(RA), "ra_current")
atlas_digest(UnityPy.load(RAB), "ra_backup")
