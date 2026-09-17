# project_status.md — Armello 中文本地化项目状态

> 最后更新：2026-09-17（字体工程收官）｜ 公开仓库仅含成品与必要工具

## 最终交付

- **游戏内全部文本**（任务/卡牌/对话/物品/成就）：霞鹜文楷正文 + 思源宋体 Heavy 标题 ✅
- **主菜单**：系统字体（微软雅黑）——代码级加载，资产 mod 无法触及，接受现状
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
- 主菜单文字：TMP SDF 图集（resources.assets.resS 单通道 @offset 11674616）已烘焙文楷 ✅
- 主菜单 Logo：定制美术字（非字体，不处理）
- 全局规范：~/.zcode/AGENTS.md（跨项目 10 条纪律）

## 遗留事项

- **Release 同步**：v0.2 font 包需更新为最新 gamedatabase（含 tc/jp/kr 文楷与菜单图集烘焙）——发 v0.3 或用户网页替换
- **艺术字分支**：马善政（OFL）已选定，等用户指令构建第三选项 zip
- **STYLE_GUIDE 存量**：英文引号 385 / 半角标点 16 / 打出了句式 2（低优先级润色）
- **旧 key 轮换**：DeepSeek 后台（不紧急）
