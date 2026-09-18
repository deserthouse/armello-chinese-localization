"""写入前全面副作用验证：test 包 vs 当前 gd（对照资产必须零变化）。只读。"""
import hashlib

import UnityPy

GD = r"D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/StreamingAssets/ResourceBundles/gamedatabase.unity3d"
TEST = "fontwork/gd_write_test.unity3d"

def collect(path):
    out = {}
    env = UnityPy.load(path)
    out["_objcount"] = len(list(env.objects))
    for obj in env.objects:
        if obj.type.name not in ("Texture2D", "MonoBehaviour", "Font"):
            continue
        try:
            d = obj.read()
            nm = d.m_Name or ""
        except Exception:
            continue
        if obj.type.name == "Texture2D" and nm.endswith("SDF Atlas"):
            out["tex:" + nm] = hashlib.md5(d.image.tobytes()[3::4]).hexdigest()
        elif obj.type.name == "MonoBehaviour" and nm in (
                "NotoSansCJKsc-Regular SDF", "SimplifiedChinese",
                "NotoSansCJKtc-Bold SDF", "TraditionalChinese"):
            out["mb:" + nm] = hashlib.md5(obj.get_raw_data()).hexdigest()
        elif obj.type.name == "Font" and nm == "NotoSansCJKsc-Regular":
            out["font:sc-Regular"] = len(bytes(d.m_FontData or b""))
    return out

a = collect(GD)
b = collect(TEST)

print(f"对象数: 原 {a['_objcount']} / 新 {b['_objcount']}")
allok = True
for k in sorted(set(a) | set(b)):
    va, vb = a.get(k), b.get(k)
    mark = "=" if va == vb else "≠≠≠"
    if va != vb:
        allok = False
    print(f"  {mark} {k}: {va} vs {vb}")
print("\n结论:", "除目标图集外全部零变化 ✅" if (
    allok and b.get("tex:NotoSansCJKsc-Regular SDF Atlas") != a.get("tex:NotoSansCJKsc-Regular SDF")) else "存在意外差异 ⚠️")
