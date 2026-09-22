<div align="center">

[简体中文](README.md) · [繁體中文](README_TC.md) · [English](README_EN.md)

<img src="docs/logo_schinese.png" width="280" alt="阿门罗"/>

# Armello 简体中文重译补丁

<img src="docs/slogan.png" width="380" alt="By Armellians, for Armellians"/>

[![License](https://img.shields.io/badge/License-Fan%20Made-blue.svg)](#-版权声明)
[![Platform](https://img.shields.io/badge/Platform-PC%20%2F%20Steam-green.svg)](#-安装使用)
[![Release](https://img.shields.io/github/v/release/deserthouse/armello-chinese-localization?include_prereleases&color=yellow&style=flat-square)](https://github.com/deserthouse/armello-chinese-localization/releases)


</div>

---

> **Armello 简体中文重译补丁** 是一个非官方粉丝项目，基于官方中文的机翻问题，对游戏内全部 10,867 条文本逐条对照英文原文重新翻译与审校——最终由 DeepSeek Pro（思考模式）拉通原文、官中与新译文三方综合审查，择优选用的 **AI 精校版文本**。

## ✨ 项目特性

### 文本质量

| 层 | 说明 |
|---|---|
| **全量覆盖** | 10,867 条：任务剧情 / 卡牌 / 物品 / UI / 成就 / 对话 / 商店 / 教学，无一遗漏 |
| **多轮 AI 精校** | Flash 初筛 → Pro 绝对质量终审（思考模式，三方对照），约 1,500 条修改 |
| **术语权威表** | 1,192 条专名强制一致 + GLOSSARY v1.2 术语规范 + STYLE_GUIDE 风格规范 |
| **格式规范化** | 占位符 / 引号 / 省略号 / 数字空格 / 换行符，程序化校验全零 |
| **决策留痕** | 每条译文携带完整 provenance 审计链，"为什么这样译"全程可溯 |

### 字体工程

| 版本 | 正文 | 标题 | 主菜单 |
|---|---|---|---|
| **font 版** | 霞鹜文楷 | 思源宋体 Heavy | 霞鹜文楷 |
| **artfont 版** | 马善政毛笔楷书 | 思源宋体 Heavy | 马善政毛笔楷书 |
| **textonly 版** | 官方原字体 | 官方原字体 | 官方原字体 |

主菜单字体通过重烘焙 TMP SDF 距离场图集实现替换（详见 [HACKING.md](HACKING.md)），正文通过 Font 对象 TTF 内嵌替换实现。全部字体均为 OFL 开源许可。

## 📸 效果预览

### font 版（霞鹜文楷）

<p float="left">
  <img src="docs/screenshots/font_mainmenu.png" width="400" alt="font 版主菜单"/>
  <img src="docs/screenshots/font_gallery.png" width="400" alt="font 版卡牌图录"/>
</p>

### artfont 版（马善政毛笔楷书）

<p float="left">
  <img src="docs/screenshots/artfont_mainmenu.png" width="400" alt="artfont 版主菜单"/>
  <img src="docs/screenshots/artfont_gallery.png" width="400" alt="artfont 版卡牌图录"/>
</p>

## 🚀 安装使用

**[📥 前往 Releases 下载最新版本](https://github.com/deserthouse/armello-chinese-localization/releases)**

三版任选其一（文本内容完全相同，区别仅在字体）：

| 版本 | 大小 | 适合 |
|---|---|---|
| **textonly** | 39.7MB | 只改文本，保持官方字体 |
| **font** | 293.9MB | 文本 + 霞鹜文楷（清爽手写楷体） |
| **artfont** | 258.5MB | 文本 + 马善政毛笔楷书（粗犷书法风） |

### 步骤

1. 下载压缩包
2. Steam 库中右键 Armello → 管理 → 浏览本地文件 → 进入 `Armello\armello_Data\`
3. 把压缩包内**全部内容**解压到 `armello_Data\`，覆盖同名文件（`StreamingAssets` 子文件夹自动落位）
4. 启动游戏

> 建议覆盖前备份原文件。还原时把备份文件改回原名即可。

### 推荐搭配：Tooltip Fix

> 🧩 **[Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix)** —— 修复游戏引擎在卡牌描述中 tooltip 链接标签跨行泄露为乱码文字的 bug。官方版本同样存在此问题，使用任何文本 mod 后更容易触发。独立安装，与本补丁完全兼容。

## ❓ 常见问题

**会影响成就或联机吗？**

不会。补丁只替换显示文本，不修改任何游戏逻辑与数值。

**font 版和 artfont 版有什么区别？**

文本内容完全相同，区别仅在于字体风格——font 版正文用霞鹜文楷（清爽易读），artfont 版用马善政毛笔楷书（视觉冲击力强，匹配中世纪奇幻画风）。选你喜欢的即可，不要混装。

**卡牌描述里偶尔看到 `[/url]` 之类的乱码？**

这是游戏引擎的 tooltip 标签跨行渲染 bug（官方版本同样存在）。安装 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) 即可修复。

**游戏更新后补丁会失效吗？**

可能。游戏大版本更新后文本结构可能变化，届时需要等本补丁适配。若更新后出现异常，先还原官方文件。

**发现错别字或翻译问题？**

欢迎提 [Issue](https://github.com/deserthouse/armello-chinese-localization/issues)，注明大概位置（哪个界面/哪张卡/哪段剧情）即可。

## 🔧 给开发者

技术笔记见 [HACKING.md](HACKING.md)——包含文本定位、UnityPy 解包重打包、SDF 字体图集替换原理等。源数据 `master.jsonl` 含全部条目及逐条决策留痕。

## 🤖 AI 使用声明

本项目不含任何人类成分，绝大多数工作都由 **AI** 完成。文本质量因此可能存在 AI 翻译的典型瑕疵，欢迎通过 Issue 反馈。

## 📄 版权声明

- 《Armello》游戏本体及其中全部原始文本、美术、音频等素材的知识产权归 **League of Geeks** 所有，本仓库维护者对上述内容**不主张任何形式的所有权**
- 本仓库不包含任何游戏本体资源，仅包含社区翻译文本与读写工具
- 本补丁为非商业粉丝项目，仅供已购买游戏的玩家个人使用，禁止将游戏文本用于商业用途或单独再分发
- 如权利方认为本仓库内容侵犯权益，请联系删除

## ⚠️ 免责声明

- 本补丁按"现状"（AS IS）提供，**不附带任何明示或默示的担保**
- 下载、安装或使用本补丁的一切风险由使用者自行承担
- 本项目与 League of Geeks 及官方无任何关联，亦不代表官方立场
- 使用本补丁即表示你已阅读并同意上述条款
