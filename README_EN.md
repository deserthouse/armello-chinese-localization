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

# Armello Chinese Localization Patch

[![License](https://img.shields.io/badge/License-Fan%20Made-blue.svg)](#-license)
[![Platform](https://img.shields.io/badge/Platform-PC%20%2F%20Steam-green.svg)](#-installation)
[![Release](https://img.shields.io/github/v/release/deserthouse/armello-chinese-localization?include_prereleases&color=yellow)](https://github.com/deserthouse/armello-chinese-localization/releases)

<sub>Simplified Chinese: full retranslation · Traditional Chinese: official-translation refinement · Fonts: three variants</sub>

</div>

<br/>

> The **Armello Chinese Localization Patch** ships two product lines in one package: the **Simplified Chinese line** retranslates all 10,867 in-game text entries from English; the **Traditional Chinese line** refines the official Traditional Chinese translation against the English source — both lines passed multi-round AI audits (word-precision / orthography / terminology unification). Text switches instantly with the in-game language setting.
>
> 🧩 Strongly recommended alongside [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix): without it, some card descriptions can trigger an engine line-wrapping bug that leaks visible `[/url]` garbled text. Independent installation, no dependency.

## ✨ Features

### Text Quality

| Line | Detail |
|---|---|
| **Simplified Chinese** | 10,867 entries retranslated from English: Flash screening → Pro final review (three-way comparison) |
| **Traditional Chinese** | Official TC as base, refined against English: word-precision fixes / typos / terminology unification (Taiwan terminology preserved) |
| **Multi-round AI review** | ~1,500 SC retranslation revisions + ~2,600 TC refinements, dual-engine cross-review + human final adjudication |
| **Terminology authority** | SC GLOSSARY v1.2.1 + TC GLOSSARY_TC v1.2 + AUDIT_ANCHORS precedent anchors |
| **Format normalization** | Placeholders, quotes, ellipses, line breaks — all programmatically zero-defect |
| **Decision audit trail** | Every entry carries full provenance — "why this translation" is fully traceable |

### Font Engineering

| Version | SC Body | SC Headings | TC Body | TC Headings | Main Menu |
|---|---|---|---|---|---|
| **textonly** | Official font | Official font | Official font | Official font | Official font |
| **font** | LXGW WenKai | Source Han Serif SC Heavy | LXGW WenKai | Source Han Serif TC Heavy | SC WenKai / TC official |
| **artfont** | Ma Shan Zheng (brush) | Source Han Serif Heavy | Official font | Official font | Ma Shan Zheng |

All fonts are licensed under SIL OFL 1.1 — copyright and authors listed in [licenses/FONT-LICENSES.txt](licenses/FONT-LICENSES.txt); the full license text ships inside the font and artfont packages.

## 📸 Screenshots

### font version (LXGW WenKai)

> 💡 You may notice an engine bug in the screenshot: a `[/url]` tag leaking as visible text in Moon Scythe's description (unrelated to the font or the translation). Install [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) to eliminate it.

<p float="left">
  <img src="docs/screenshots/font_mainmenu.png" width="400" alt="font version main menu"/>
  <img src="docs/screenshots/font_gallery.png" width="400" alt="font version card gallery"/>
</p>

### artfont version (Ma Shan Zheng brush calligraphy)

<p float="left">
  <img src="docs/screenshots/artfont_mainmenu.png" width="400" alt="artfont version main menu"/>
  <img src="docs/screenshots/artfont_gallery.png" width="400" alt="artfont version card gallery"/>
</p>

## 🚀 Installation

**[📥 Download from Releases](https://github.com/deserthouse/armello-chinese-localization/releases)**

Choose one of three versions (both SC and TC text are always included; only fonts differ):

| Version | Size | Best for |
|---|---|---|
| **textonly** | 39.3MB | Text only, keep official fonts |
| **font** | 309MB | Text + LXGW WenKai (SC/TC) + Source Han Serif headings (SC/TC variants) |
| **artfont** | 254.9MB | Text + SC Ma Shan Zheng brush calligraphy (TC falls back to official fonts) |

### Steps

1. Download the zip
2. In Steam, right-click Armello → Manage → Browse Local Files → open `Armello\armello_Data\`
3. Extract **all contents** of the zip into `armello_Data\`, overwriting existing files (the `StreamingAssets` subfolder will be placed automatically)
4. Launch the game, switch language in settings (简体中文 / 繁體中文)

> Back up original files before overwriting. To restore, rename backups back.

### Recommended: Tooltip Fix

> 🧩 **[Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix)** — Fixes an engine bug where tooltip link tags in card descriptions leak as visible garbled text. Present in the official version too. Independent installation, fully compatible with this patch.

## ❓ FAQ

**Can I use both Simplified and Traditional Chinese?**

Yes. Both languages' text are packed in the same resources.assets — switch languages anytime in-game.

**Does this affect achievements or multiplayer?**

No. The patch only replaces display text — no game logic or values are modified.

**What's the difference between font and artfont versions?**

Text content is identical (both SC and TC lines). Font version uses LXGW WenKai (clean, readable). Artfont version uses Ma Shan Zheng (bold brush calligraphy) for Simplified Chinese body text; Traditional Chinese falls back to official fonts. Pick your preference; do not mix.

**Which version should a Traditional Chinese player choose?**

- Refined text only → **textonly**
- WenKai body + Taiwan-standard Source Han Serif headings → **font**
- Sharing artfont with an SC player → TC automatically uses official fonts

**I see `[/url]` garbled text in card descriptions.**

This is a game engine bug (present in official version too). Install [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) to fix it.

**Will this break after a game update?**

Possibly. Text structure may change in major updates. Restore official files if issues arise.

**Found a typo or translation issue?**

Please open an [Issue](https://github.com/deserthouse/armello-chinese-localization/issues) with the location (which screen/card/quest).

## 🔧 For Developers

See [HACKING.md](HACKING.md) for technical details — text location, UnityPy unpack/repack, SDF atlas replacement. Source data in `master.jsonl` includes full per-entry decision audit trail.

## 🤖 AI Usage Disclosure

This project contains no human contribution; the vast majority of the work was done by **AI**. AI translation quirks may exist — feedback via Issue is welcome.

## 📄 License

- All rights to Armello, its original text, art, and audio belong to **League of Geeks**. This repository claims **no ownership** of any game content.
- This repository contains no binary game assets (code, art, audio); it does contain text data extracted from the game (English source and official Simplified/Traditional Chinese) used solely for translation cross-reference and per-entry auditing, plus read/write tooling.
- Screenshots and official promotional logos are used for documentation purposes; all copyrights belong to League of Geeks.
- This is a non-commercial fan project for personal use by players who have purchased the game. Redistribution of game text separately is prohibited.
- If the rights holder believes this repository infringes their rights, please contact for removal.

## ⚠️ Disclaimer

- This patch is provided "AS IS", **without warranty of any kind**.
- Users assume all risks from downloading, installing, or using this patch.
- This project is not affiliated with League of Geeks or the official Armello team.
- Use of this patch constitutes acceptance of these terms.
