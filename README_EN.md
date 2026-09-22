<div align="center">

[简体中文](README.md) · [繁體中文](README_TC.md) · [English](README_EN.md)

<img src="docs/logo_english.png" width="280" alt="Armello"/>

# Armello Chinese Relocalization

<img src="docs/slogan.png" width="380" alt="By Armellians, for Armellians"/>

[![License](https://img.shields.io/badge/License-Fan%20Made-blue.svg)](#-license)
[![Platform](https://img.shields.io/badge/Platform-PC%20%2F%20Steam-green.svg)](#-installation)
[![Release](https://img.shields.io/github/v/release/deserthouse/armello-chinese-localization?include_prereleases&color=yellow&style=flat-square)](https://github.com/deserthouse/armello-chinese-localization/releases)


</div>

---

> **Armello Chinese Relocalization** is an unofficial fan project that retranslates all 10,867 in-game text entries from English, addressing the official Chinese translation's machine-translation quality issues. Final text is curated by DeepSeek Pro (thinking mode) with three-way comparison of English source, official Chinese, and the new translation — an **AI-refined edition**.

## ✨ Features

### Text Quality

| Layer | Detail |
|---|---|
| **Full coverage** | 10,867 entries: quests, cards, items, UI, achievements, dialogue, store, tutorials |
| **Multi-pass AI review** | Flash screening → Pro absolute-quality final review (thinking mode, three-way comparison), ~1,500 revisions |
| **Terminology authority** | 1,192 proper noun mappings + GLOSSARY v1.2 + STYLE_GUIDE |
| **Format normalization** | Placeholders, quotes, ellipses, number spacing, line breaks — all programmatically zero-defect |
| **Decision audit trail** | Every entry carries full provenance — "why this translation" is fully traceable |

### Font Engineering

| Version | Body | Headings | Main Menu |
|---|---|---|---|
| **font** | LXGW WenKai | Source Han Serif Heavy | LXGW WenKai |
| **artfont** | Ma Shan Zheng (brush calligraphy) | Source Han Serif Heavy | Ma Shan Zheng |
| **textonly** | Official font | Official font | Official font |

Main menu font replacement is achieved by re-baking the TMP SDF distance-field atlas (see [HACKING.md](HACKING.md)). All fonts are OFL open-source licensed.

## 📸 Screenshots

### font version (LXGW WenKai)

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

Choose one of three versions (text content is identical, only fonts differ):

| Version | Size | Best for |
|---|---|---|
| **textonly** | 42MB | Text only, keep official fonts |
| **font** | 308MB | Text + LXGW WenKai (clean handwriting style) |
| **artfont** | 271MB | Text + Ma Shan Zheng (bold brush calligraphy) |

### Steps

1. Download the zip
2. In Steam, right-click Armello → Manage → Browse Local Files → open `Armello\armello_Data\`
3. Extract **all contents** of the zip into `armello_Data\`, overwriting existing files (the `StreamingAssets` subfolder will be placed automatically)
4. Launch the game

> Back up original files before overwriting. To restore, rename backups back.

### Recommended: Tooltip Fix

> 🧩 **[Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix)** — Fixes an engine bug where tooltip link tags in card descriptions leak as visible garbled text. Present in the official version too. Independent installation, fully compatible with this patch.

## ❓ FAQ

**Does this affect achievements or multiplayer?**

No. The patch only replaces display text — no game logic or values are modified.

**What's the difference between font and artfont versions?**

Text content is identical. Font version uses LXGW WenKai (clean, readable). Artfont version uses Ma Shan Zheng (bold brush calligraphy, matching the medieval fantasy aesthetic). Pick your preference; do not mix.

**I see `[/url]` garbled text in card descriptions.**

This is a game engine bug (present in official version too). Install [Armello Tooltip Fix](https://github.com/deserthouse/armello-tooltip-fix) to fix it.

**Will this break after a game update?**

Possibly. Text structure may change in major updates. Restore official files if issues arise.

**Found a typo or translation issue?**

Please open an [Issue](https://github.com/deserthouse/armello-chinese-localization/issues) with the location (which screen/card/quest).

## 🔧 For Developers

See [HACKING.md](HACKING.md) for technical details — text location, UnityPy unpack/repack, SDF atlas replacement. Source data in `master.jsonl` includes full per-entry decision audit trail.

## 🤖 AI Usage Disclosure

The vast majority of translation, review, and engineering work on this project was performed by **AI (large language models)**. The human role is requirements, decision-making, and final acceptance. AI translation quirks may exist — feedback via Issue is welcome.

## 📄 License

- All rights to Armello, its original text, art, and audio belong to **League of Geeks**. This repository claims **no ownership** of any game content.
- This repository contains no game assets — only community translations and tooling.
- This is a non-commercial fan project for personal use by players who have purchased the game. Redistribution of game text separately is prohibited.
- If the rights holder believes this repository infringes their rights, please contact for removal.

## ⚠️ Disclaimer

- This patch is provided "AS IS", **without warranty of any kind**.
- Users assume all risks from downloading, installing, or using this patch.
- This project is not affiliated with League of Geeks or the official Armello team.
- Use of this patch constitutes acceptance of these terms.
