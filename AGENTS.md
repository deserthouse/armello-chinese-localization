# armello-chinese-localization 项目规范

> Armello 非官方简体中文**全量重译**补丁：对 10,867 条文本逐条对照英文重译审校（替换 resources.assets）。**Pre-Release v0.2 已发布**（github.com/deserthouse/armello-chinese-localization），Issue 反馈驱动维护。
> 只替换显示文本，不碰游戏逻辑与数值。全局规范见 `~/.zcode/AGENTS.md`。

## 数据与流水线

- **单一真源 = `master.jsonl`**（每条 `id/en/zh_official/zh/status/provenance`）；CSV/HTML/补丁全部是再生品，由 `pipeline.py`（审计/导出）与 `repack.py`（打包）生成，可重复执行。
- 权威分诊计数（总 10,867）：locked 4,480 | unaudited 4,172 | untranslated 2,203 | added 12；终态 final_ok 9,725 / final_official 1,138 / final_r1 4。
- 标准资产四件套是质量 SSOT：GLOSSARY.md（+json 双版本）、STYLE_GUIDE.md、REVIEW_SPEC、pipeline.py 三道 QA；**元规则：每轮发现的系统性问题必须回写资产，否则下轮重犯**。
- 审查判决留档在本地 git 分支 `archive-full-history`（查判决用 `git show`，不在工作树）。
- `review_merge` 重跑会把全部历史判决重新套用覆盖后续修正——"改了又被改回去"先查这个。
- 数据坑三条（勿当缺陷修）：QUEST_RAT / WOLF_PROLOGUE_AI_1/2 三条 ID 串位系原版提取错位；"勇士们"是合法 warriors 复数；菜单"卡牌图鉴"→"卡牌图集"（官方 SDF 图集 2,859 字符集缺"鉴"字）。

## 字体工程（font 包）

- 正文=霞鹜文楷 Regular（12.5MB，OFL，lxgw v1.520）、标题=思源宋体 Heavy（wght=900 实例化）；管线 = fontTools instancer 实例化 → Subsetter 子集化（语料 3,124 字 + 基本汉字区）→ 修 name 表；**必须同时补丁 resources.assets 和 gamedatabase.unity3d 两处**。
- 主菜单中文是**系统微软雅黑**（Unity 内置 Arial → OS 字体链接，资产 mod 不可及）——菜单字体调查已收官，剩余收尾两步见项目记忆 menu-font-saga（fontwork/wenkai_identity.png 三合一对照 + tc 副本 glyphIndex 金丝雀）。
- TMP 二进制硬解：16B/条字符表 + 36B/条 unicode 直键矩形表（2,752 条）；**非对齐扫描**（表起始 mod4=3，按 4 对齐读 word 全漏）；金丝雀用 glyphIndex 等长替换最安全。
- SDF 烘焙口径：2048²，alpha 通道 SDF，官方口径 0~173/边缘 128，含 6× 超采样 + scipy EDT；Texture2D 写入 `d.set_image(PIL.Image)`（RGBA32 无损）。
- UnityPy：read_typetree 返回真文本 str，直接赋值写回（`tt["m_Script"] = csv_content`），手工 latin-1 包装=双重编码乱码（v1.0 事故根源）；读 CSV 用 `utf-8-sig` 剥 BOM。
- 恢复基底：resources.assets.backup / gamedatabase.unity3d.backup。

## API 与密钥

- DeepSeek key 走环境变量 `DEEPSEEK_API_KEY` 或 gitignore 的 `api_key.local`（当前 key 余额有限，用前确认）；模型参数见全局规范九.5。
- 翻译流水线按全局规范九执行：Flash 初翻（关思考）→ Pro 审校（开思考）→ 程序化 QA → 人工抽检；术语表 + STYLE_GUIDE + 邻居上下文注入。

## 发布

- 双包：font.zip 231MB / textonly.zip 41.6MB；zip 打包用 PowerShell Compress-Archive（本项目是 PC 分发，不受 Android 刷机包限制约束）。
- GitHub OAuth token（gho_）用 `Authorization: Bearer`；**DELETE release 资产对该 token 恒 404**（权限残缺 GitHub 故意 404 不说 403）——替换资产要么用户网页删、要么发新 tag；PATCH release body 可能持续 502（读正常写 502），文档类修改优先走 git push。
- 公开仓用 orphan 分支重置为单次干净提交；key 被 Push Protection 拦 → filter-branch 重写而非放行。
- 合规：不主张游戏素材所有权、仓库不含本体资源、非商业粉丝项目、仅限已购买玩家、AS IS、AI 使用声明（绝大部分翻译审校由 AI 完成，人类做需求/决策/验收）。
- 与 armello-android-revived 的衔接：复活计划第 5 步并入本汉化成果。
