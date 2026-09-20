# Armello 汉化补丁·技术笔记

> 给想了解本补丁如何运作、或想在此基础上做贡献的开发者。不需要读完本文也能正常使用补丁。

## 文本在哪里

Armello 的全部游戏文本存储在 `armello_Data/resources.assets` 内的一个 TextAsset（名称 `SimplifiedChinese`）中，格式为**两列 CSV**（`ID,SimplifiedChinese`），约 10,867 条。每种语言各一个 TextAsset（English / SimplifiedChinese / TraditionalChinese / Japanese / Korean 等），互不干扰。

游戏启动后按当前语言设置加载对应 TextAsset，以 `ID` 为键查询显示。因此修改这个 TextAsset 即可完成全部文本替换，不影响游戏逻辑。

## 如何解包与重打包

使用 [UnityPy](https://github.com/K0lbos/UnityPy)（Python 库）读写 Unity 资产文件：

```python
import UnityPy

env = UnityPy.load("resources.assets")
for obj in env.objects:
    if obj.type.name == "TextAsset":
        data = obj.read()
        if data.m_Name == "SimplifiedChinese":
            # 读出当前文本（CSV 格式的 str）
            csv_content = data.m_Script

            # 写入修改后的文本
            tt = obj.read_typetree()
            tt["m_Script"] = new_csv_content
            obj.save_typetree(tt)

# 保存整个资产文件
blob = env.file.save()
open("resources_assets_new", "wb").write(blob)
```

**注意事项**：
- CSV 编码为 UTF-8（读取时用 `utf-8-sig` 剥 BOM）
- `read_typetree()` 返回的 `m_Script` 是真正的 Python `str`，直接赋值写回即可；不要手工做 latin-1 包装（会导致双重编码乱码）
- 保存后文件可能被 Python 进程自身锁定，需要在**另一个进程**中执行 `os.replace` 替换原文件

## 字体替换（进阶）

Armello 使用两套字体渲染系统：

| 系统 | 用途 | 修改方式 |
|---|---|---|
| Unity Font（TTF 内嵌） | 游戏内正文/标题 | 替换 Font 对象的 `m_FontData` 字段（TTF 字节流） |
| TextMeshPro SDF 图集 | 主菜单/UI | 重烘焙 SDF 图集纹理（见下文） |

**主菜单 SDF 图集**是本补丁最复杂的部分。原理：TMP（TextMeshPro）不直接使用 TTF 渲染，而是预烘焙每个字形为带符号距离场（SDF）像素图集，打包在 `gamedatabase.unity3d` 资源包内。替换步骤：

1. 从 `gamedatabase.unity3d` 提取 TMP_FontAsset（MonoBehaviour）获取字符表 → 图集格位映射
2. 用目标字体逐字渲染 → 生成 SDF（`scipy.ndimage.distance_transform_edt`，6× 超采样）
3. 按原始格位布局写回图集（需**垂直翻转**，Unity 纹理为左下原点）
4. 同步写入 `resources.assets.resS`（在线渲染路径）和 `gamedatabase.unity3d` 内嵌 resS（离线路径）

**关键坑**：
- `UnityPy` 的 `Texture2D.set_image()` 对单通道外部 resS 纹理**静默失效**——必须直接覆写 resS 文件中的数据块
- resS 中的像素是**垂直翻转**的（左下原点），写入前需 `[::-1]`
- SDF 边缘阈值约 128，内部饱和值约 173（非 255）

## 术语与风格规范

- `GLOSSARY.md`：核心术语对照表（属性/资源/种族/地名/物品等）
- `STYLE_GUIDE.md`：风格规范（引号/省略号/数字空格/署名格式/风味文规则等）
- 修改译文时请遵守这两份规范；发现新的系统性问题请回写规范（防止后续轮次重犯）

## 数据格式

`master.jsonl` 是全部条目的单一真源，每行一个 JSON 对象：

```json
{
  "id": "MAINMENU_CONTINUELABEL",
  "en": "Continue",
  "zh_official": "继续",
  "zh": "继续",
  "status": "final_ok",
  "provenance": [...]
}
```

`provenance` 数组记录了该条目经历的每一轮处理（翻译引擎/审校/修改及理由），是完整的决策审计链。

## Issue 反馈格式

提 Issue 时请注明：
- 大概位置（哪个界面/哪张卡/哪段剧情）
- 当前译文是什么、期望是什么（如有的话）

我们会对照英文原文和官中核查后修正。
