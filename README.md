<div align="center">

[简体中文](README.md) · [繁體中文](README_TC.md) · [English](README_EN.md)

<img src="docs/logo_en_main.png" width="300" alt="Armello"/>

<br/>

<p>
  <img src="docs/logo_schinese.png" height="130" alt="阿门罗"/>
  <img src="docs/logo_dot_v3.png" height="130" alt="·"/>
  <img src="docs/logo_tc.png" height="130" alt="愛門羅"/>
</p>

<img src="docs/slogan.png" width="380" alt="By Armellians, for Armellians"/>

# Armello 中文本地化补丁

[![License](https://img.shields.io/badge/License-Fan%20Made-blue.svg)](#-版权声明)
[![Platform](https://img.shields.io/badge/Platform-PC%20%2F%20Steam-green.svg)](#-安装使用)
[![Release](https://img.shields.io/github/v/release/deserthouse/armello-chinese-localization?include_prereleases&color=yellow)](https://github.com/deserthouse/armello-chinese-localization/releases)

<sub>简体中文 · 全量重译 ｜ 繁体中文 · 官方译本精修 ｜ 中文字体 · 三档替换</sub>

</div>

<br/>

> **Armello 中文本地化补丁** 包含简繁双线产品：**简中线**对游戏内全部 10,867 条文本逐条对照英文原文重新翻译与审校；**繁中线**以官方繁中为底本，逐条对照英文原文精修错漏——两线均经 AI 多轮全量审校（词义偏移 / 正字 / 术语统一），文本随游戏内语言切换即时生效。
>
> 🧩 强烈建议同时安装 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix)：否则部分卡牌描述会触发游戏引擎的换行渲染 bug，外显 `[/url]` 乱码文字。两者独立安装、互不依赖。

## ✨ 项目特性

### 文本质量

| 线 | 说明 |
|---|---|
| **简中·全量重译** | 10,867 条：逐条对照英文原文重译，Flash 初筛 → Pro 终审（三方对照） |
| **繁中·官方精修** | 以官方繁中为底，逐条对照英文精修词义偏移 / 错字 / 术语统一（台版术语体系保留） |
| **AI 多轮精校** | 简中 ~1,500 条重译修改 + 繁中 ~2,600 条精修，双引擎互审 + 人工终审 |
| **术语权威表** | 简中 GLOSSARY v1.2.1 + 繁中 GLOSSARY_TC v1.2 + AUDIT_ANCHORS 判例锚点 |
| **格式规范化** | 占位符 / 引号 / 省略号 / 换行符，程序化校验全零 |
| **决策留痕** | 每条译文携带完整 provenance 审计链 |

### 字体工程

| 版本 | 语言 | 正文 | 标题 | 主菜单 |
|---|---|---|---|---|
| **textonly** | 简中 | 官方原字体 | 官方原字体 | 官方原字体 |
| | 繁中 | 官方原字体 | 官方原字体 | 官方原字体 |
| **font** | 简中 | 霞鹜文楷 | 思源宋体 SC Heavy | 霞鹜文楷 |
| | 繁中 | 霞鹜文楷 | 思源宋体 TC Heavy | 官方原黑体 |
| **artfont** | 简中 | 马善政毛笔楷书 | 思源宋体 Heavy | 马善政毛笔楷书 |
| | 繁中 | 莫大毛筆字體 | 思源宋体 TC Heavy | 官方原黑体 |

> **繁中主菜单与图标在三个版本下均保持官方黑体**——为维持繁中界面图标与主菜单字体的视觉一致性，繁中菜单体系不做替换。

全部字体均为 SIL OFL 1.1 开源许可，版权与作者见 [licenses/FONT-LICENSES.txt](licenses/FONT-LICENSES.txt)，许可全文随 font 与 artfont 安装包附带。包内嵌字体为子集化衍生版，含保留字体名的字体已按 OFL 条款改名（ArmelloBrushTC / ArmelloSerifTC），版权声明保留。

### 字体致谢

| 字体 | 作者 / 项目 | 许可 | 上游 |
|---|---|---|---|
| 霞鹜文楷 | LXGW（基于 Fontworks Klee One） | OFL 1.1 | [lxgw/LxgwWenKai](https://github.com/lxgw/LxgwWenKai) |
| 思源宋体 SC / TC | Adobe + Google | OFL 1.1 | [adobe-fonts/source-han-serif](https://github.com/adobe-fonts/source-han-serif) |
| 马善政毛笔楷书 | MaShanZheng Project Authors | OFL 1.1 | [googlefonts/mashanzheng](https://github.com/googlefonts/mashanzheng) |
| 莫大毛筆字體 | Chun yu Yao（基于青柳衡山「衡山毛筆フォント」） | OFL 1.1 | [max32002/bakudaifont](https://github.com/max32002/bakudaifont) |

## 📸 效果预览

### font 版（霞鹜文楷）

> 💡 截图中可注意到一处游戏引擎 bug：月亮镰刀的效果文本外显了 `[/url]` 标签（与字体和翻译无关）。安装 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) 即可消除。

<p float="left">
  <img src="docs/screenshots/font_mainmenu.png" width="400" alt="font 版主菜单"/>
  <img src="docs/screenshots/font_gallery.png" width="400" alt="font 版卡牌图录"/>
</p>

### artfont 版（简中马善政 / 繁中莫大毛筆體）

<p float="left">
  <img src="docs/screenshots/artfont_mainmenu.png" width="400" alt="artfont 版主菜单"/>
  <img src="docs/screenshots/artfont_gallery.png" width="400" alt="artfont 版卡牌图录"/>
</p>

## 🚀 安装使用

**[📥 前往 Releases 下载最新版本](https://github.com/deserthouse/armello-chinese-localization/releases)**

三版任选其一（简繁双语文本均内置，区别仅在字体）：

| 版本 | 大小 | 适合 |
|---|---|---|
| **textonly** | 39.3MB | 只改文本，保持官方字体 |
| **font** | 303.6MB | 文本 + 霞鹜文楷（简繁）+ 思源宋体标题（简繁各 SC/TC） |
| **artfont** | 243.3MB | 文本 + 简中马善政毛笔楷书 + 繁中莫大毛笔字體（繁中标题思源宋体 TC） |

- **textonly**——原版字体原汁原味，仅替换翻译文本：适合只想要新汉化文本、不想改动官方字体观感的玩家。
- **font**——正文选用霞鹜文楷（楷书笔意的现代字体，字形圆润温和、久读不累），标题选用思源宋体 Heavy（笔画厚重的宋体，自带碑刻般的分量感）：正文有温度、标题有气势，适合想在**艺术效果与可读性之间取得平衡**的玩家。
- **artfont**——正文整体换装毛笔书法字体（简中马善政毛笔楷书、繁中莫大毛筆字體），笔墨韵味最浓，最贴合阿门罗的奇幻绘本气质；代价是手写笔迹的字形辨识度不及印刷体系字体，可读性逊于 font 版：适合更看重**艺术表现**、愿意为风格让渡一点阅读速度的玩家。

### 步骤

1. 下载压缩包
2. Steam 库中右键 Armello → 管理 → 浏览本地文件 → 进入 `Armello\armello_Data\`
3. 把压缩包内**全部内容**解压到 `armello_Data\`，覆盖同名文件（`StreamingAssets` 子文件夹自动落位）
4. 启动游戏，在设置中切换语言（简体中文 / 繁體中文）

> 建议覆盖前备份原文件。还原时把备份文件改回原名即可。

## ❓ 常见问题

**简中和繁中可以同时使用吗？**

可以。两个语言的文本都打包在同一个 resources.assets 里，游戏内随时切换语言即可。

**会影响成就或联机吗？**

不会。补丁只替换显示文本，不修改任何游戏逻辑与数值。

**font 版和 artfont 版有什么区别？**

文本内容完全相同（简繁双线），区别仅在于字体风格——font 版正文用霞鹜文楷（清爽易读），artfont 版简中正文用马善政毛笔楷书、繁中正文用莫大毛笔字體（视觉冲击力强）。选你喜欢的即可，不要混装。

**繁中玩家该选哪个版本？**

- 只想要精修文本 → **textonly**
- 想要文楷正文 + 台标思源宋体标题 → **font**
- 想要毛笔书法风格正文 + 台标思源宋体标题 → **artfont**（繁中正文 = 莫大毛笔字體）

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
- 本仓库不含游戏的代码、美术、音频等二进制资源；包含从游戏提取的文本数据（英文原文与官方简繁译文），仅用于翻译对照与逐条审计，及其读写工具
- 页面截图与官方宣传 Logo 系文档目的的合理引用，版权归 League of Geeks 所有
- 本补丁为非商业粉丝项目，仅供已购买游戏的玩家个人使用，禁止将游戏文本用于商业用途或单独再分发
- 如权利方认为本仓库内容侵犯权益，请联系删除

## ⚠️ 免责声明

- 本补丁按"现状"（AS IS）提供，**不附带任何明示或默示的担保**
- 下载、安装或使用本补丁的一切风险由使用者自行承担
- 本项目与 League of Geeks 及官方无任何关联，亦不代表官方立场
- 使用本补丁即表示你已阅读并同意上述条款
