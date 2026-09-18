# project_status.md — Armello 中文本地化项目状态

> 最后更新：2026-09-17（字体工程收官）｜ 公开仓库仅含成品与必要工具

## 最终交付

- **游戏内全部文本**（任务/卡牌/对话/物品/成就）：霞鹜文楷正文 + 思源宋体 Heavy 标题 ✅
- **主菜单**：仍为原版 Noto Sans CJK SC（TMP SDF，外观酷似雅黑）。真源=gamedatabase 包内 SDF 图集（09-18 证实，旧"系统雅黑/代码级加载"结论已证伪）；旧烘焙误落 resources.assets 孤儿副本。修复路径已明确，待批准执行
- **10,867 条译文**：全量重译 + 四版本对照终审 ✅
- **Release**：v0.2 双包已上线（font 版 231MB / textonly 版 42MB），v0.2 font 包需更新为最新（含 tc/jp/kr 文楷替换与菜单图集烘焙）

## 架构

```
master.jsonl —— 唯一真源（10,867 条 + provenance 逐条留痕）
pipeline.py   —— init/translate/review_split/review_merge/export
repack.py     —— 写回游戏 resources.assets（优先读 export CSV）
GLOSSARY.md v1.1 + STYLE_GUIDE.md —— 标准资产
fontwork/     —— 字体工程（子集/烘焙/图集，git 忽略）
```

## 字体工程结论

- 游戏内动态文本：Font 对象 TTF 替换 ✅（文楷/文楷 Medium）
- 主菜单文字：TMP SDF 真源在 **gamedatabase 包内**（字符表+图集同包，LanguageAsset 绑定）；resources.assets 那份是孤儿副本，旧烘焙（ra.resS @11674616 文楷+捐献格鉴）对菜单无效——gd 当前与备份逐字节相同证实从未生效
- 主菜单 Logo：定制美术字（非字体，不处理）
- 全局规范：~/.zcode/AGENTS.md（跨项目 10 条纪律）

## 遗留事项

- **主菜单字体修复（方案已定，待批准）**：把文楷 SDF 烘焙进 gamedatabase 包内 sc 图集（必要时捐献格加"鉴"于 gd TMP 字符表，可顺带恢复"卡牌图鉴"措辞）；烘焙脚本/探针在 tests/menu_font_probe_*.py
- **Release 同步**：v0.2 font 包需更新为最新 gamedatabase（含 tc/jp/kr 文楷与菜单图集烘焙）——发 v0.3 或用户网页替换（若执行菜单字体修复，合并进 v0.3 一起发）
- **艺术字分支**：马善政（OFL）已选定，等用户指令构建第三选项 zip
- **STYLE_GUIDE 存量**：英文引号 385 / 半角标点 16 / 打出了句式 2（低优先级润色）
- **旧 key 轮换**：DeepSeek 后台（不紧急）
