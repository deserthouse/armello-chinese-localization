"""探针A：gamedatabase.unity3d 内部——SDF 资产清单 + 谁在引用 sc SDF。只读。"""
import struct

import UnityPy

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"

env = UnityPy.load(GD)
objs = list(env.objects)
print("total objects:", len(objs))

# 1) 全部 Font + SDF 相关资产清单
fonts_all = []
sdf_assets = {}
for obj in objs:
    if obj.type.name not in ("MonoBehaviour", "Texture2D", "Material", "Font"):
        continue
    try:
        name = obj.read().m_Name or ""
    except Exception:
        continue
    if obj.type.name == "Font":
        fonts_all.append((obj.path_id, name))
    if "SDF" in name or name in ("Font Material", "Font Texture"):
        sdf_assets.setdefault((name, obj.type.name), obj.path_id)

print("\n-- all Font objects --")
for pid, name in sorted(fonts_all, key=lambda x: x[1]):
    print(f"  pid={pid:<22} {name}")
print("\n-- SDF-ish assets --")
for (name, t), pid in sorted(sdf_assets.items()):
    print(f"  {t:14s} pid={pid:<22} {name}")

sc_font_pid = sdf_assets.get(("NotoSansCJKsc-Regular SDF", "MonoBehaviour"))
sc_atlas_pid = sdf_assets.get(("NotoSansCJKsc-Regular SDF Atlas", "Texture2D"))

def scan_refs(target_pid, label):
    print(f"\n-- refs to {label} (pid={target_pid}) --")
    pat = struct.pack("<q", target_pid)
    n = 0
    for obj in objs:
        if obj.path_id == target_pid:
            continue
        try:
            raw = obj.get_raw_data()
        except Exception:
            continue
        if pat in raw:
            try:
                nm = obj.read().m_Name
            except Exception:
                nm = "?"
            n += 1
            if n <= 30:
                print(f"   {obj.type.name:14s} pid={obj.path_id:<22} {nm}")
    print(f"   total {n}")

scan_refs(sc_font_pid, "sc SDF TMP asset")
scan_refs(sc_atlas_pid, "sc SDF Atlas")
