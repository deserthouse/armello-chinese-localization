<div align="center">

[簡體中文](README.md) · [繁體中文](README_TC.md) · [English](README_EN.md)

<img src="docs/logo_en_main.png" width="300" alt="Armello"/>

<br/>

<p>
  <img src="docs/logo_schinese.png" height="130" alt="阿门罗"/>
  <img src="docs/logo_dot_v3.png" height="130" alt="·"/>
  <img src="docs/logo_tc.png" height="130" alt="愛門羅"/>
</p>

<img src="docs/slogan.png" width="380" alt="By Armellians, for Armellians"/>

# Armello 中文本地化補丁

[![License](https://img.shields.io/badge/License-Fan%20Made-blue.svg)](#-版權聲明)
[![Platform](https://img.shields.io/badge/Platform-PC%20%2F%20Steam-green.svg)](#-安裝使用)
[![Release](https://img.shields.io/github/v/release/deserthouse/armello-chinese-localization?include_prereleases&color=yellow)](https://github.com/deserthouse/armello-chinese-localization/releases)

<sub>簡體中文 · 全量重譯 ｜ 繁體中文 · 官方譯本精修 ｜ 中文字型 · 三檔替換</sub>

</div>

<br/>

> **Armello 中文本地化補丁** 包含簡繁雙線產品：**簡中線**對遊戲內全部 10,867 條文字逐條對照英文原文重新翻譯與審校；**繁中線**以官方繁中為底本，逐條對照英文原文精修錯漏——兩線均經 AI 多輪全量審校（詞義偏移 / 正字 / 術語統一），文字隨遊戲內語言切換即時生效。
>
> 🧩 強烈建議同時安裝 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix)：否則部分卡牌描述會觸發遊戲引擎的換行渲染 bug，外顯 `[/url]` 亂碼文字。兩者獨立安裝、互不依賴。

## ✨ 專案特性

### 文字品質

| 線 | 說明 |
|---|---|
| **簡中·全量重譯** | 10,867 條：逐條對照英文原文重譯，Flash 初篩 → Pro 終審（三方對照） |
| **繁中·官方精修** | 以官方繁中為底，逐條對照英文精修詞義偏移 / 錯字 / 術語統一（台版術語體系保留） |
| **AI 多輪精校** | 簡中 ~1,500 條重譯修改 + 繁中 ~2,600 條精修，雙引擎互審 + 人工終審 |
| **術語權威表** | 簡中 GLOSSARY v1.2.1 + 繁中 GLOSSARY_TC v1.2 + AUDIT_ANCHORS 判例錨點 |
| **格式規範化** | 佔位符 / 引號 / 省略號 / 換行符，程式化校驗全零 |
| **決策留痕** | 每條譯文攜帶完整 provenance 審計鏈 |

### 字型工程

| 版本 | 語言 | 正文 | 標題 | 主選單 |
|---|---|---|---|---|
| **textonly** | 簡中 | 官方原字型 | 官方原字型 | 官方原字型 |
| | 繁中 | 官方原字型 | 官方原字型 | 官方原字型 |
| **font** | 簡中 | 霞鶩文楷 | 思源宋體 SC Heavy | 霞鶩文楷 |
| | 繁中 | 霞鶩文楷 | 思源宋體 TC Heavy | 官方原黑體 |
| **artfont** | 簡中 | 馬善政毛筆楷書 | 思源宋體 Heavy | 馬善政毛筆楷書 |
| | 繁中 | 莫大毛筆字體 | 思源宋體 TC Heavy | 官方原黑體 |

> **繁中主選單與圖示在三個版本下均保持官方黑體**——為維持繁中介面圖示與主選單字型的視覺一致性，繁中選單體系不做替換。

全部字型均為 SIL OFL 1.1 開源授權，版權與作者見 [licenses/FONT-LICENSES.txt](licenses/FONT-LICENSES.txt)，授權全文隨 font 與 artfont 安裝包附帶。包內嵌字型為子集化衍生版，含保留字型名的字型已按 OFL 條款改名（ArmelloBrushTC / ArmelloSerifTC），版權聲明保留。

### 字型致謝

| 字型 | 作者 / 專案 | 授權 | 上游 |
|---|---|---|---|
| 霞鶩文楷 | LXGW（基於 Fontworks Klee One） | OFL 1.1 | [lxgw/LxgwWenKai](https://github.com/lxgw/LxgwWenKai) |
| 思源宋體 SC / TC | Adobe + Google | OFL 1.1 | [adobe-fonts/source-han-serif](https://github.com/adobe-fonts/source-han-serif) |
| 馬善政毛筆楷書 | MaShanZheng Project Authors | OFL 1.1 | [googlefonts/mashanzheng](https://github.com/googlefonts/mashanzheng) |
| 莫大毛筆字體 | Chun yu Yao（基於青柳衡山「衡山毛筆フォント」） | OFL 1.1 | [max32002/bakudaifont](https://github.com/max32002/bakudaifont) |

## 📸 效果預覽

### font 版（霞鶩文楷）

> 💡 截圖中可注意到一處遊戲引擎 bug：月亮鐮刀的效果文字外顯了 `[/url]` 標籤（與字型和翻譯無關）。安裝 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) 即可消除。

<p float="left">
  <img src="docs/screenshots/font_mainmenu.png" width="400" alt="font 版主選單"/>
  <img src="docs/screenshots/font_gallery.png" width="400" alt="font 版卡牌圖錄"/>
</p>

### artfont 版（簡中馬善政 / 繁中莫大毛筆字體）

<p float="left">
  <img src="docs/screenshots/artfont_mainmenu.png" width="400" alt="artfont 版主選單"/>
  <img src="docs/screenshots/artfont_gallery.png" width="400" alt="artfont 版卡牌圖錄"/>
</p>

## 🚀 安裝使用

**[📥 前往 Releases 下載最新版本](https://github.com/deserthouse/armello-chinese-localization/releases)**

三版任選其一（簡繁雙語文字均內建，區別僅在字型）：

| 版本 | 大小 | 適合 |
|---|---|---|
| **textonly** | 39.3MB | 只改文字，保持官方字型 |
| **font** | 309MB | 文字 + 霞鶩文楷（簡繁）+ 思源宋體標題（簡繁各 SC/TC） |
| **artfont** | 254.7MB | 文字 + 簡中馬善政毛筆楷書 + 繁中莫大毛筆字體（繁中標題思源宋體 TC） |

### 步驟

1. 下載壓縮包
2. Steam 庫中右鍵 Armello → 管理 → 瀏覽本地檔案 → 進入 `Armello\armello_Data\`
3. 把壓縮內**全部內容**解壓到 `armello_Data\`，覆蓋同名檔案（`StreamingAssets` 子資料夾自動落位）
4. 啟動遊戲，在設定中切換語言（簡體中文 / 繁體中文）

> 建議覆蓋前備份原檔案。還原時把備份檔案改回原名即可。

## ❓ 常見問題

**簡中和繁中可以同時使用嗎？**

可以。兩個語言的文字都打包在同一個 resources.assets 裡，遊戲內隨時切換語言即可。

**會影響成就或連線嗎？**

不會。補丁只替換顯示文字，不修改任何遊戲邏輯與數值。

**font 版和 artfont 版有什麼區別？**

文字內容完全相同（簡繁雙線），區別僅在於字型風格——font 版正文用霞鶩文楷（清爽易讀），artfont 版簡中正文用馬善政毛筆楷書、繁中正文用莫大毛筆字體（視覺衝擊力強）。選你喜歡的即可，不要混裝。

**繁中玩家該選哪個版本？**

- 只想要精修文字 → **textonly**
- 想要文楷正文 + 台標思源宋體標題 → **font**
- 想要毛筆書法風格正文 + 台標思源宋體標題 → **artfont**（繁中正文 = 莫大毛筆字體）

**卡牌描述裡偶爾看到 `[/url]` 之類的亂碼？**

這是遊戲引擎的 tooltip 標籤跨行渲染 bug（官方版本同樣存在）。安裝 [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) 即可修復。

**遊戲更新後補丁會失效嗎？**

可能。遊戲大版本更新後文字結構可能變化，屆時需要等本補丁適配。若更新後出現異常，先還原官方檔案。

**發現錯別字或翻譯問題？**

歡迎提 [Issue](https://github.com/deserthouse/armello-chinese-localization/issues)，註明大概位置（哪個介面/哪張卡/哪段劇情）即可。

## 🔧 給開發者

技術筆記見 [HACKING.md](HACKING.md)——包含文字定位、UnityPy 解包重打包、SDF 字型圖集替換原理等。源資料 `master.jsonl` 含全部條目及逐條決策留痕。

## 🤖 AI 使用宣告

本專案不含任何人類成分，絕大多數工作都由 **AI** 完成。文字品質因此可能存在 AI 翻譯的典型瑕疵，歡迎透過 Issue 回饋。

## 📄 版權聲明

- 《Armello》遊戲本體及其中全部原始文字、美術、音訊等素材的智慧財產權歸 **League of Geeks** 所有，本倉庫維護者對上述內容**不主張任何形式的所有權**
- 本倉庫不含遊戲的程式碼、美術、音訊等二進位資源；包含從遊戲提取的文字資料（英文原文與官方簡繁譯文），僅用於翻譯對照與逐條審計，及其讀寫工具
- 頁面截圖與官方宣傳 Logo 係文件目的的合理引用，版權歸 League of Geeks 所有
- 本補丁為非商業粉絲專案，僅供已購買遊戲的玩家個人使用，禁止將遊戲文字用於商業用途或單獨再分發
- 如權利方認為本倉庫內容侵犯權益，請聯絡刪除

## ⚠️ 免責聲明

- 本補丁按「現狀」（AS IS）提供，**不附帶任何明示或默示的擔保**
- 下載、安裝或使用本補丁的一切風險由使用者自行承擔
- 本專案與 League of Geeks 及官方無任何關聯，亦不代表官方立場
- 使用本補丁即表示你已閱讀並同意上述條款
